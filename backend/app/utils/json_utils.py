import numpy as np

def sanitize_json(obj):
    """
    Recursively clean data for JSON serialization, replacing NaN/Inf with None.
    """
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    return obj
