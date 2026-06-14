import numpy as np
import pandas as pd
from typing import List, Dict, Any
from app.services.anomaly_detector import AnomalyDetector
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

class EvaluationService:
    @staticmethod
    def inject_synthetic_anomalies(data: List[Dict[str, Any]], fraction: float = 0.05) -> List[Dict[str, Any]]:
        """
        Injects synthetic anomalies into a fraction of data points for evaluation.
        Sets 'ground_truth' and 'is_injected' keys for each record.
        """
        if not data:
            return []

        df = pd.DataFrame(data)
        np.random.seed(42)

        std_price = df['close'].std()

        n_anomalies = max(1, int(len(df) * fraction)) if fraction > 0 else 0
        anomaly_indices = np.random.choice(df.index, size=n_anomalies, replace=False)

        df['ground_truth'] = False

        for idx in anomaly_indices:
            anomaly_type = np.random.choice([0, 1, 2])

            if anomaly_type == 0:
                spike = 3 * std_price * np.random.uniform(0.8, 1.2)
                df.at[idx, 'close'] += spike
                df.at[idx, 'high'] = max(df.at[idx, 'high'], df.at[idx, 'close'])
            elif anomaly_type == 1:
                drop = 3 * std_price * np.random.uniform(0.8, 1.2)
                df.at[idx, 'close'] = max(df.at[idx, 'close'] - drop, df.at[idx, 'close'] * 0.1)
                df.at[idx, 'low'] = min(df.at[idx, 'low'], df.at[idx, 'close'])
            else:
                historical_vol_max = df['volume'].rolling(10, min_periods=1).max().loc[idx]
                if historical_vol_max == 0 or np.isnan(historical_vol_max):
                    historical_vol_max = df['volume'].mean()
                df.at[idx, 'volume'] = max(df.at[idx, 'volume'] * 5, historical_vol_max * np.random.uniform(2, 5))

            df.at[idx, 'ground_truth'] = True

        return df.to_dict(orient='records')

    @staticmethod
    def evaluate_models(data: List[Dict[str, Any]], fraction: float = 0.05, models: List[str] = ['isolation_forest', 'lof', 'ocsvm', 'autoencoder']) -> Dict[str, Any]:
        """
        Evaluates multiple anomaly detection models using injected synthetic anomalies.
        """
        test_data = EvaluationService.inject_synthetic_anomalies(data, fraction=fraction)

        y_true = [row['ground_truth'] for row in test_data]

        if not test_data or len(y_true) == 0:
            return {}

        results = {}
        for model in models:
            try:
                preds_data = AnomalyDetector.detect_anomalies(test_data, model_type=model)
                y_pred = [res['is_anomaly'] for res in preds_data]

                if len(y_pred) != len(y_true):
                    raise ValueError(f"Prediction length mismatch for model {model}.")

                precision = precision_score(y_true, y_pred, zero_division=0)
                recall = recall_score(y_true, y_pred, zero_division=0)
                f1 = f1_score(y_true, y_pred, zero_division=0)
                cm = confusion_matrix(y_true, y_pred, labels=[False, True])

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
