import numpy as np
import pandas as pd
from typing import List, Dict, Any
from app.services.anomaly_detector import AnomalyDetector
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

class EvaluationService:
    @staticmethod
    def inject_synthetic_anomalies(data: List[Dict[str, Any]], fraction: float = 0.05) -> List[Dict[str, Any]]:
        """
        Kopiuje bazowe dane i wstrzykuje wybranemu ułamkowi z nich kontrolowane anomalie dla ceny lub wolumenu.
        Dodaje do wszystkich rekordów klucz 'ground_truth' określający czy to była ta anomalia i 'is_injected'.
        """
        if not data:
            return []
            
        # Pracujemy na głębokiej kopii, aby nie powielać wariantów z mutacjami do podstawowego środowiska.
        df = pd.DataFrame(data)
        np.random.seed(42) # Dla względnej powtarzalności wyników, można pominąć zależnie od strategii ewaluacji zespołu.
        
        # Wyliczamy standardowe odchylenie używane do naturalniejszych modyfikacji cen
        std_price = df['close'].std()
        
        n_anomalies = max(1, int(len(df) * fraction)) if fraction > 0 else 0
        anomaly_indices = np.random.choice(df.index, size=n_anomalies, replace=False)
        
        df['ground_truth'] = False
        
        # Tworzenie anomalnego zachowania
        for idx in anomaly_indices:
            # Losujemy rodzaj anomalii: 0 - skok ceny, 1 - spadek ceny, 2 - ekstremalny popyt (wolumen)
            anomaly_type = np.random.choice([0, 1, 2])
            
            if anomaly_type == 0:
                # Skok cenowy = close rośnie np o +3 st.odch
                spike = 3 * std_price * np.random.uniform(0.8, 1.2)
                df.at[idx, 'close'] += spike
                # Aktualizacja High, bo zamkniecie moglo wyjsc poza
                df.at[idx, 'high'] = max(df.at[idx, 'high'], df.at[idx, 'close']) 
            elif anomaly_type == 1:
                # Upadek cenowy = close maleje np. o -3 st.odch
                drop = 3 * std_price * np.random.uniform(0.8, 1.2)
                # Unikamy zejscia ponizej minimalnych poziomow (0)
                df.at[idx, 'close'] = max(df.at[idx, 'close'] - drop, df.at[idx, 'close'] * 0.1) 
                # Aktualizacja Low dla integralnosci swiecy
                df.at[idx, 'low'] = min(df.at[idx, 'low'], df.at[idx, 'close'])
            else:
                # Ogromny napływ wolumenu (np. x5 do piku 10-dniowego), by algorytmy dostrzegły też wolumenowe różnice
                historical_vol_max = df['volume'].rolling(10, min_periods=1).max().loc[idx]
                if historical_vol_max == 0 or np.isnan(historical_vol_max):
                    historical_vol_max = df['volume'].mean()
                df.at[idx, 'volume'] = max(df.at[idx, 'volume'] * 5, historical_vol_max * np.random.uniform(2, 5))
                
            df.at[idx, 'ground_truth'] = True

        return df.to_dict(orient='records')
        
    @staticmethod
    def evaluate_models(data: List[Dict[str, Any]], fraction: float = 0.05, models: List[str] = ['isolation_forest', 'lof', 'ocsvm', 'autoencoder']) -> Dict[str, Any]:
        """
        Inicjuje obieg dla każdej testowanej modyfikacji. Przeprowadza pełną ewaluacje standardowych miar ze scikit-learn.
        """
        # Przygotowanie kopii zbioru danych z anomaliami na wspólny proces testowania
        test_data = EvaluationService.inject_synthetic_anomalies(data, fraction=fraction)
        
        # Prawdziwe etykiety ukryte po wstrzyknięciu (False/True)
        y_true = [row['ground_truth'] for row in test_data]
        
        if not test_data or len(y_true) == 0:
            return {}

        results = {}
        for model in models:
            # Ponieważ klasa AnomalyDetector dopisuje wszystkie kolumny matematyki z powrotem i tworzy dicty, 
            # wyciągniemy z powrotem stąd 'is_anomaly'.
            # WAŻNE: detect_anomalies filtruje out do valid_output_cols. Etykieta 'ground_truth' 
            # na pewno poleci z wyniku API, więc my operujemy na y_true wyliczonym linijkę wczesniej. 
            # Wystarczy odzyskać ich przelicznik is_anomaly.
            
            try:
                # Ewaluujemy jeden, wybrany algorytm
                preds_data = AnomalyDetector.detect_anomalies(test_data, model_type=model)
                y_pred = [res['is_anomaly'] for res in preds_data]
                
                if len(y_pred) != len(y_true):
                    raise ValueError(f"Długość zbioru predykcji {model} jest asymetryczna wobec wejścia.")
                
                # Używamy zzero_division aby uniknąć błędów przy pustym secie True w TP 
                precision = precision_score(y_true, y_pred, zero_division=0)
                recall = recall_score(y_true, y_pred, zero_division=0)
                f1 = f1_score(y_true, y_pred, zero_division=0)
                cm = confusion_matrix(y_true, y_pred, labels=[False, True])
                
                # Skompresowana do sensownego JSON struktury macierz
                tn, fp, fn, tp = cm.ravel()
                
                results[model] = {
                    "metrics": {
                        "precision": precision,
                        "recall": recall,
                        "f1_score": f1
                    },
                    "confusion_matrix": {
                        "true_negatives": int(tn),
                        "false_positives": int(fp),
                        "false_negatives": int(fn),
                        "true_positives": int(tp)
                    },
                    "summary": {
                        "total_anomalies_detect": int(fp + tp),
                        "total_ground_truth": int(fn + tp)
                    }
                }
            except Exception as e:
                results[model] = {
                    "error": str(e)
                }
                
        return {
            "evaluation": results,
            "metadata": {
                "total_records": len(y_true),
                "injected_fraction": fraction
            }
        }
