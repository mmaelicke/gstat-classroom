"""
"""
import os
import numpy as np
from imageio import imread
import base64
import hashlib

DATAPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


def create_random_3d(seed=42) -> dict:
    """Random dummy 3D data"""
    np.random.seed(seed)
    coords = np.random.gamma(14, 6, size=(150, 3))
    np.random.seed(seed)
    values = np.random.gamma(150, 2, size=(150))

    return dict(
        coordinates=coords, 
        values=values
    )


def pancake(fname='pancake1.png', seed=None, n=600) -> dict:
    """Delicious Pancake"""
    # load the image
    img = imread(os.path.join(DATAPATH, fname))

    # use only red channel
    data = img[:,:,0]

    # sample the pancake
    np.random.seed(seed=seed)
    coords = np.random.randint([0,0], data.shape, size=(n, 2))
    vals = np.fromiter((data[c[0], c[1]] for c in coords), dtype=int)

    return dict(
        coordinates=coords,
        values=vals,
#        imgSrc=b64
        original2D=data
    )


# TODO: This can be replaced by an instance of a class managing the data
# i.e. caching the hashs into a in-memory sqlite database
# for now, this stays static
def __create_dataset(func, *args, **kwargs):
    # run the dataset creator
    result_dict = func(*args, **kwargs)

    # hash the result
    h = hashlib.sha256(str(result_dict).encode()).hexdigest()

    return h, result_dict


CREATORS = [create_random_3d, pancake]

DATA = {k: v for k,v in [__create_dataset(create_func, seed=42) for create_func in CREATORS]}

DATASETS = {k:func.__doc__.split('\n')[0] for k, func in [(h, f) for h,f in zip(DATA.keys(), CREATORS)]}
