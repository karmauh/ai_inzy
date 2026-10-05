import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Sequence
from app.services.anomaly_detector import AnomalyDetector, SUPPORTED_MODELS
from app.services.data_processor import DataProcessor
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix


class EvaluationService:
    @staticmethod
    def inject_synthetic_anomalies(data: List[Dict[str, Any]], fraction: float = 0.05, seed: int = 42) -> List[Dict[str, Any]]:
        """
        Wstrzykuje syntetyczne anomalie (skok ceny, spadek ceny, skok wolumenu) do części punktów.
        Ustawia klucz 'ground_truth' dla każdego rekordu i przelicza wskaźniki techniczne,
        aby odzwierciedlały zmodyfikowane notowania.
        """
        if not data:
            return []

        df = pd.DataFrame(data)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

        rng = np.random.default_rng(seed)
        std_price = df['close'].std()

        # Ta sama liczba co punktów oznaczanych przez modele (AnomalyDetector.flag_top_fraction)
        n_anomalies = min(len(df), max(1, int(np.ceil(len(df) * fraction)))) if fraction > 0 else 0
        anomaly_indices = rng.choice(df.index, size=n_anomalies, replace=False)

        df['ground_truth'] = False

        for idx in anomaly_indices:
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

            df.at[idx, 'ground_truth'] = True

        # Wskaźniki muszą być spójne ze zmodyfikowanymi cenami
        df = DataProcessor.add_technical_indicators(df)
        df = df.astype(object).where(pd.notnull(df), None)

        return df.to_dict(orient='records')

    @staticmethod
    def evaluate_models(data: List[Dict[str, Any]], fraction: float = 0.05, models: Optional[Sequence[str]] = None, n_runs: int = 10) -> Dict[str, Any]:
        """
        Ocenia wiele modeli detekcji anomalii na danych z wstrzykniętymi syntetycznymi anomaliami.
        Ewaluacja jest powtarzana n_runs razy (seed 0..n_runs-1 – inne miejsca i typy anomalii),
        a metryki raportowane są jako średnia i odchylenie standardowe. Wszystkie modele oceniają
        te same zestawy danych testowych. Parametr contamination modeli odpowiada frakcji anomalii.
        """
        models = list(models) if models else list(SUPPORTED_MODELS)
        runs = [EvaluationService.inject_synthetic_anomalies(data, fraction=fraction, seed=seed) for seed in range(n_runs)]
        if not runs or not runs[0]:
            return {}

        results = {}
        for model in models:
            try:
                metrics_per_run, cm_per_run = [], []
                for test_data in runs:
                    y_true = [bool(row['ground_truth']) for row in test_data]
                    y_pred = [res['is_anomaly'] for res in AnomalyDetector.detect_anomalies(test_data, model_type=model, contamination=fraction)]

                    if len(y_pred) != len(y_true):
                        raise ValueError(f"Prediction length mismatch for model {model}.")

                    metrics_per_run.append([
                        precision_score(y_true, y_pred, zero_division=0),
                        recall_score(y_true, y_pred, zero_division=0),
                        f1_score(y_true, y_pred, zero_division=0),
                    ])
                    cm_per_run.append(confusion_matrix(y_true, y_pred, labels=[False, True]).ravel())

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
                "injected_fraction": fraction,
                "n_runs": n_runs
            }
        }
