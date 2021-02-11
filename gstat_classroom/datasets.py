"""
"""
import numpy as np


def create_random_3d() -> dict:
    np.random.seed(42)
    coords = np.random.gamma(14, 6, size=(150, 3))
    np.random.seed(42)
    values = np.random.gamma(150, 2, size=(150))

    return dict(
        coordinates=coords, 
        values=values
    )
