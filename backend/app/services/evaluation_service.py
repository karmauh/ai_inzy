import logging
import os
import threading
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Sequence, Tuple
from app.services.anomaly_detector import AnomalyDetector, SUPPORTED_MODELS, WALK_FORWARD_MIN_TRAIN
from app.services.data_processor import DataProcessor
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

logger = logging.getLogger(__name__)

# Pula procesów dla benchmarku walk-forward (dziesiątki douczeń modelu na przebieg).
# Procesy, a nie wątki: budowa drzew Isolation Forest trzyma GIL, więc wątki nie przyspieszały obliczeń.
# Pula tworzona jest leniwie i utrzymywana między zapytaniami (start procesu z torchem trwa ~1-2 s).
_POOL: Optional[ProcessPoolExecutor] = None
_POOL_LOCK = threading.Lock()


def _worker_count() -> int:
    return max(1, int(os.getenv("EVALUATION_WORKERS", min(6, os.cpu_count() or 1))))


def _get_pool() -> ProcessPoolExecutor:
    global _POOL
    with _POOL_LOCK:
        if _POOL is None:
            _POOL = ProcessPoolExecutor(max_workers=_worker_count())
        return _POOL


def shutdown_pool(wait: bool = True) -> None:
    """Zamyka pulę procesów (wywoływane przy zatrzymaniu aplikacji lub po awarii puli)."""
    global _POOL
    with _POOL_LOCK:
        if _POOL is not None:
            _POOL.shutdown(wait=wait, cancel_futures=True)
        _POOL = None


def _predict(task: Tuple[str, List[Dict[str, Any]], float, str]):
    """Detekcja dla jednej pary (model, przebieg). Błąd zwracany jako tekst, by nie przerywał ewaluacji."""
    model, test_data, fraction, mode = task
    try:
        return AnomalyDetector.detect_anomalies(test_data, model_type=model, contamination=fraction, mode=mode)
    except Exception as e:
        return f"{type(e).__name__}: {e}"


def _predict_all(tasks: List[Tuple[str, List[Dict[str, Any]], float, str]], parallel: bool) -> list:
    if parallel and _worker_count() > 1:
        try:
            return list(_get_pool().map(_predict, tasks))
        except BrokenProcessPool:
            logger.exception("Pula procesów ewaluacji uległa awarii – obliczenia sekwencyjne")
            shutdown_pool(wait=False)
    return [_predict(task) for task in tasks]


SCENARIOS = ('basic', 'extended')
POINT_TYPES = ('price_spike', 'price_drop', 'volume_spike', 'gap_reversal')
COLLECTIVE_TYPES = ('drift', 'volatility_burst')
# Liczba kolejnych sesji objętych anomalią wielosesyjną
COLLECTIVE_LENGTH = 5
# Wybuch zmienności: odchylenie szumu zamknięć i poszerzenie zakresu dnia (w dziennych sigmach)
VOLATILITY_BURST_NOISE = 2.0
VOLATILITY_BURST_RANGE = 1.0


def _mark(df: pd.DataFrame, indices, anomaly_type: str, event_id: int) -> None:
    df.loc[indices, 'ground_truth'] = True
    df.loc[indices, 'anomaly_type'] = anomaly_type
    df.loc[indices, 'anomaly_event'] = event_id


def _inject_basic(df: pd.DataFrame, rng: np.random.Generator, start_index: int, budget: int) -> None:
    """Pojedyncze, duże anomalie (3 odchylenia standardowe poziomu ceny) – scenariusz pierwotny."""
    std_price = df['close'].std()
    for event_id, idx in enumerate(rng.choice(df.index[start_index:], size=budget, replace=False)):
        anomaly_type = rng.integers(0, 3)

        if anomaly_type == 0:
            spike = 3 * std_price * rng.uniform(0.8, 1.2)
            df.at[idx, 'close'] += spike
            df.at[idx, 'high'] = max(df.at[idx, 'high'], df.at[idx, 'close'])
        elif anomaly_type == 1:
            drop = 3 * std_price * rng.uniform(0.8, 1.2)
            df.at[idx, 'close'] = max(df.at[idx, 'close'] - drop, df.at[idx, 'close'] * 0.1)
            df.at[idx, 'low'] = min(df.at[idx, 'low'], df.at[idx, 'close'])
        else:
            historical_vol_max = df['volume'].rolling(10, min_periods=1).max().loc[idx]
            if historical_vol_max == 0 or np.isnan(historical_vol_max):
                historical_vol_max = df['volume'].mean()
            df.at[idx, 'volume'] = max(df.at[idx, 'volume'] * 5, historical_vol_max * rng.uniform(2, 5))

        _mark(df, [idx], ('price_spike', 'price_drop', 'volume_spike')[anomaly_type], event_id)


def _inject_extended(df: pd.DataFrame, rng: np.random.Generator, start_index: int, budget: int) -> None:
    """
    Anomalie skalowane do dziennej zmienności stóp zwrotu (sigma), punktowe i wielosesyjne.
    Zdarzenia nie nachodzą na siebie (co najmniej jedna sesja odstępu).
    """
    sigma = df['close'].pct_change().std()
    sigma = sigma if np.isfinite(sigma) and sigma > 0 else 0.01
    n = len(df)
    occupied = np.zeros(n, dtype=bool)
    event_id = 0
    attempts = 0

    while budget > 0 and attempts < 1000:
        attempts += 1
        collective = budget >= COLLECTIVE_LENGTH and rng.random() < 0.5
        anomaly_type = rng.choice(COLLECTIVE_TYPES if collective else POINT_TYPES)
        length = COLLECTIVE_LENGTH if collective else 1

        # Luka wymaga poprzedniej sesji, dryf przesuwa także sesje późniejsze
        first = max(start_index, 1)
        if n - length < first:
            break
        idx = int(rng.integers(first, n - length + 1))
        window = range(idx, idx + length)
        if occupied[max(0, idx - 1):min(n, idx + length + 1)].any():
            continue

        if anomaly_type == 'price_spike' or anomaly_type == 'price_drop':
            # Ruch ceny zamknięcia o 4-6 dziennych odchyleń standardowych
            sign = 1 if anomaly_type == 'price_spike' else -1
            df.at[idx, 'close'] *= 1 + sign * rng.uniform(4, 6) * sigma
            df.at[idx, 'high'] = max(df.at[idx, 'high'], df.at[idx, 'close'])
            df.at[idx, 'low'] = min(df.at[idx, 'low'], df.at[idx, 'close'])
        elif anomaly_type == 'volume_spike':
            df.at[idx, 'volume'] *= rng.uniform(3, 6)
        elif anomaly_type == 'gap_reversal':
            # Otwarcie daleko od poprzedniego zamknięcia, zamknięcie bez zmian (długi korpus/cień świecy)
            sign = rng.choice([-1, 1])
            df.at[idx, 'open'] = df.at[idx - 1, 'close'] * (1 + sign * rng.uniform(4, 6) * sigma)
            df.at[idx, 'high'] = max(df.at[idx, 'high'], df.at[idx, 'open'])
            df.at[idx, 'low'] = min(df.at[idx, 'low'], df.at[idx, 'open'])
        elif anomaly_type == 'drift':
            # Każda sesja dokłada 1-1.5 sigma w tym samym kierunku; żadna osobno nie jest skrajna.
            # Późniejsze sesje przesuwamy o skumulowany ruch (trwała zmiana poziomu, bez sztucznego powrotu).
            daily = rng.choice([-1, 1]) * rng.uniform(1.0, 1.5) * sigma
            factors = np.cumprod(np.full(length, 1 + daily))
            price_cols = ['open', 'high', 'low', 'close']
            for offset, factor in enumerate(factors):
                df.loc[idx + offset, price_cols] *= factor
            df.loc[idx + length:, price_cols] *= factors[-1]
        else:  # volatility_burst
            # Zamknięcia szarpane dodatkowym szumem i szerszy zakres dnia, poziom ceny bez zmian
            for i in window:
                df.at[i, 'close'] *= 1 + rng.normal(0, VOLATILITY_BURST_NOISE * sigma)
                df.at[i, 'high'] = max(df.at[i, 'high'] * (1 + VOLATILITY_BURST_RANGE * sigma), df.at[i, 'close'], df.at[i, 'open'])
                df.at[i, 'low'] = min(df.at[i, 'low'] * (1 - VOLATILITY_BURST_RANGE * sigma), df.at[i, 'close'], df.at[i, 'open'])

        occupied[idx:idx + length] = True
        _mark(df, list(window), str(anomaly_type), event_id)
        event_id += 1
        budget -= length


class EvaluationService:
    @staticmethod
    def inject_synthetic_anomalies(data: List[Dict[str, Any]], fraction: float = 0.05, seed: int = 42, start_index: int = 0,
                                   scenario: str = 'basic') -> List[Dict[str, Any]]:
        """
        Wstrzykuje syntetyczne anomalie do sesji o indeksie >= start_index; łączna liczba sesji
        oznaczonych jako anomalie to frakcja tego zakresu.
        - 'basic': pojedyncze skoki ceny / spadki ceny / skoki wolumenu o wielkości 3 odchyleń
          standardowych poziomu ceny z całego okresu (łatwe do wykrycia).
        - 'extended': anomalie skalowane do dziennej zmienności instrumentu, w tym zdarzenia
          wielosesyjne (dryf, wybuch zmienności) i nietypowe świece (luka z powrotem).
        Ustawia klucze 'ground_truth', 'anomaly_type' i 'anomaly_event' (id zdarzenia) dla każdego
        rekordu i przelicza wskaźniki techniczne, aby odzwierciedlały zmodyfikowane notowania.
        """
        if not data:
            return []
        if scenario not in SCENARIOS:
            raise ValueError(f"Unsupported scenario: {scenario}")

        df = pd.DataFrame(data)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

        rng = np.random.default_rng(seed)
        df['ground_truth'] = False
        df['anomaly_type'] = None
        df['anomaly_event'] = None

        n_candidates = len(df) - start_index
        # Ta sama liczba sesji co punktów oznaczanych przez modele (AnomalyDetector.flag_top_fraction)
        budget = min(n_candidates, max(1, int(np.ceil(n_candidates * fraction)))) if fraction > 0 and n_candidates > 0 else 0

        if scenario == 'basic':
            _inject_basic(df, rng, start_index, budget)
        else:
            _inject_extended(df, rng, start_index, budget)

        # Wskaźniki muszą być spójne ze zmodyfikowanymi cenami
        df = DataProcessor.add_technical_indicators(df)
        df = df.astype(object).where(pd.notnull(df), None)

        return df.to_dict(orient='records')

    @staticmethod
    def evaluate_models(data: List[Dict[str, Any]], fraction: float = 0.05, models: Optional[Sequence[str]] = None,
                        n_runs: int = 10, mode: str = 'batch', scenario: str = 'basic') -> Dict[str, Any]:
        """
        Ocenia wiele modeli detekcji anomalii na danych z wstrzykniętymi syntetycznymi anomaliami.
        Ewaluacja jest powtarzana n_runs razy (seed 0..n_runs-1 – inne miejsca i typy anomalii),
        a metryki raportowane są jako średnia i odchylenie standardowe. Wszystkie modele oceniają
        te same zestawy danych testowych. Parametr contamination modeli odpowiada frakcji anomalii.
        W trybie walk-forward anomalie trafiają tylko do sesji ocenianych (po okresie rozruchu),
        a metryki liczone są wyłącznie na tych sesjach.
        'by_type' podaje dla każdego typu anomalii odsetek wykrytych zdarzeń – zdarzenie (również
        wielosesyjne) uznaje się za wykryte, jeśli model oznaczył co najmniej jedną z jego sesji.
        """
        models = list(models) if models else list(SUPPORTED_MODELS)
        if mode == 'walk_forward' and len(data) <= WALK_FORWARD_MIN_TRAIN:
            raise ValueError(f"Walk-forward mode requires more than {WALK_FORWARD_MIN_TRAIN} data points.")
        start_index = WALK_FORWARD_MIN_TRAIN if mode == 'walk_forward' else 0
        runs = [EvaluationService.inject_synthetic_anomalies(data, fraction=fraction, seed=seed, start_index=start_index,
                                                             scenario=scenario)
                for seed in range(n_runs)]
        if not runs or not runs[0]:
            return {}

        # Walk-forward jest kosztowny (douczanie modelu co kilka sesji) – liczony równolegle w procesach.
        # Batch jest szybki, więc narzut przesyłania danych do procesów by się nie opłacał.
        tasks = [(model, test_data, fraction, mode) for model in models for test_data in runs]
        outputs = _predict_all(tasks, parallel=(mode == 'walk_forward'))
        predictions = {model: outputs[i * len(runs):(i + 1) * len(runs)] for i, model in enumerate(models)}

        results = {}
        for model in models:
            try:
                metrics_per_run, cm_per_run = [], []
                events_total, events_detected = {}, {}
                for test_data, preds in zip(runs, predictions[model]):
                    if isinstance(preds, str):
                        raise ValueError(preds)
                    if len(preds) != len(test_data):
                        raise ValueError(f"Prediction length mismatch for model {model}.")

                    # Pomijamy sesje nieocenione przez model (okres rozruchu w trybie walk-forward)
                    scored = [i for i, res in enumerate(preds) if res['anomaly_score'] is not None]
                    y_true = [bool(test_data[i]['ground_truth']) for i in scored]
                    y_pred = [preds[i]['is_anomaly'] for i in scored]

                    metrics_per_run.append([
                        precision_score(y_true, y_pred, zero_division=0),
                        recall_score(y_true, y_pred, zero_division=0),
                        f1_score(y_true, y_pred, zero_division=0),
                    ])
                    cm_per_run.append(confusion_matrix(y_true, y_pred, labels=[False, True]).ravel())

                    # Wykrywalność zdarzeń w podziale na typ anomalii
                    events = {}
                    for i, row in enumerate(test_data):
                        if row['ground_truth']:
                            events.setdefault(row['anomaly_event'], (row['anomaly_type'], []))[1].append(i)
                    for anomaly_type, indices in events.values():
                        events_total[anomaly_type] = events_total.get(anomaly_type, 0) + 1
                        detected = any(preds[i]['is_anomaly'] for i in indices)
                        events_detected[anomaly_type] = events_detected.get(anomaly_type, 0) + int(detected)

                mean, std = np.mean(metrics_per_run, axis=0), np.std(metrics_per_run, axis=0)
                # Macierz pomyłek: średnia liczba przypadków na jeden przebieg
                tn, fp, fn, tp = np.mean(cm_per_run, axis=0)

                results[model] = {
                    "metrics": {"precision": float(mean[0]), "recall": float(mean[1]), "f1_score": float(mean[2])},
                    "metrics_std": {"precision": float(std[0]), "recall": float(std[1]), "f1_score": float(std[2])},
                    "confusion_matrix": {
                        "true_negatives": round(float(tn), 1),
                        "false_positives": round(float(fp), 1),
                        "false_negatives": round(float(fn), 1),
                        "true_positives": round(float(tp), 1)
                    },
                    "summary": {
                        "total_anomalies_detect": round(float(fp + tp), 1),
                        "total_ground_truth": round(float(fn + tp), 1)
                    },
                    "by_type": {
                        anomaly_type: {
                            "detection_rate": events_detected[anomaly_type] / total,
                            "events": total
                        }
                        for anomaly_type, total in sorted(events_total.items())
                    }
                }
            except Exception as e:
                results[model] = {
                    "error": str(e)
                }

        return {
            "evaluation": results,
            "metadata": {
                "total_records": len(runs[0]),
                "scored_records": len(runs[0]) - start_index,
                "injected_fraction": fraction,
                "n_runs": n_runs,
                "mode": mode,
                "scenario": scenario
            }
        }
