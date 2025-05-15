import numpy as np

def fit_combo_scaler(x):
    median_x = np.median(x)
    iqr_x = np.percentile(x, 75) - np.percentile(x, 25)
    robust_x = (x - median_x) / iqr_x

    min_robust = np.nanmin(robust_x)
    max_robust = np.nanmax(robust_x)

    scaled_x = ((robust_x - min_robust) / (max_robust - min_robust)) * 2 - 1

    # Return both scaled data and parameters for future use
    return scaled_x, {
        'median': median_x,
        'iqr': iqr_x,
        'min_robust': min_robust,
        'max_robust': max_robust
    }

def combo_scaler(x, params):
    # Step 1: Robust scaling
    robust_x = (x - params['median']) / params['iqr']

    # Step 2: Min-max scaling to [-1, 1]
    scaled_x = ((robust_x - params['min_robust']) / (params['max_robust'] - params['min_robust'])) * 2 - 1

    return scaled_x

def inverse_combo_scaler(scaled_x, params):
    # Step 1: Undo min-max scaling
    robust_x = ((scaled_x + 1) / 2) * (params['max_robust'] - params['min_robust']) + params['min_robust']

    # Step 2: Undo robust scaling
    original_x = robust_x * params['iqr'] + params['median']

    return original_x