# settings
MODELS = {
    'spherical': 'Spherical',
    'exponential': 'Exponential',
    'gaussian': 'Gaussian',
    'matern': 'Matérn',
    'cubic': 'Cubic Model',
    'stable': 'Stable model'
}

ESTIMATORS = {
    'matheron': 'Matheron',
    'cressie': 'Cressie-Hawkins',
    'dowd': 'Dowd',
    'genton': 'Genton',
    'entropy': 'Shannon Entropy',
    'minmax': 'MinMax (experimental)'
}

BINNING = {
    'even': 'N Evenly spaced bins',
    'uniform': 'N uniform sized bins',
    'kmeans': 'N KMeans clustered bins',
    'ward': 'N hierachical clustered bins',
    'sturges': "Sturge's rule calculated N",
    'scott': "Scott's rule calculated N",
    'doane': "Doane's rule calculated N",
    'fd': "Calculate N by Freedman-Diaconis Estimator",
    'sqrt': "Calculate N by square-root"
}

FITTING = {
    'trf': 'Trust-Region Reflective (bounded least-squares)',
    'lm': 'Levenberg-Marquard (fast, unbounded least-squares)',
    'ml': 'SQSLP algorithm (bounded maximum likelihood)',
}

FITTING_WEIGHTS = {
    'none': 'No weighting',
    'linear': 'Linear derease with distance',
    'sq': 'Decrease by distance**2',
    'sqrt': 'Decrease by distance**0.5',
    'exp': 'Decrease by exp(distance)',
    'entropy': 'Weighted by Shannon Entropy (uncertainty)'
}
