"""
"""
import os
import numpy as np
from imageio import imread
import base64
import hashlib
from datetime import datetime as dt
from datetime import timedelta as td

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
        original2D=data
    )


class DataManager:
    CREATORS = [create_random_3d, pancake]
    DATA = {}
    DATANAMES = {}
    VARIOGRAM = {}
    KRIGING = {}

    def __init__(self, seed=42):
        self.DATA = {k: v for k,v in [self.__create_dataset(create_func, seed=seed) for create_func in self.CREATORS]}
        self.DATANAMES = {k:func.__doc__.split('\n')[0] for k, func in [(h, f) for h,f in zip(self.DATA.keys(), self.CREATORS)]}

    def get_names(self) -> dict:
        return self.DATANAMES

    def get_data(self, name) -> dict:
        return self.DATA.get(name)
    
    def get_variogram(self, name) -> dict:
        return self.VARIOGRAM.get(name)

    def get_kriging(self, name) -> dict:
        return self.KRIGING.get(name)

    def add_data(self, name=None, **kwargs):
        h, result_dict = self.__create_dataset(**kwargs)

        # set the new data
        self.DATA[h] = result_dict

        if name is None:
            name = f'Custom dataset added {dt.utcnow()}'
        self.DATANAMES[h] = name

    def add_variogram(self, variogram):
        # remove variograms which are too old
        self._check_old_variogram()
        
        # build the needed hash
        d = dict(c=variogram.coordinates, v=variogram.values, p=variogram.describe(flat=True))
        h = hashlib.sha256(str(d).encode()).hexdigest()

        # store the variogram
        self.VARIOGRAM[h] = dict(dtime=dt.utcnow(), v=variogram.clone())

        return h

    def add_kriging(self, field, sigma=None):
        # remove krigings which are too old
        self._check_old_kriging()

        # build the needed hash
        d = dict(field=field, sigma=sigma)
        h = hashlib.sha256(str(d).encode()).hexdigest()

        # store the field
        self.KRIGING[h] = dict(dtime=dt.utcnow(), data=d)

        return h

    def remove_variogram(self, h):
        if h in self.VARIOGRAM.keys():
            del self.VARIOGRAM[h]

    def remove_kriging(self, h):
        if h in self.KRIGING.keys():
            del self.KRIGING[h]

    def _check_old_variogram(self, since_hours=2):
        # create the timestamp
        since = dt.utcnow() - td(hours=since_hours)
        
        # remove everything older than since
        for h, data in self.VARIOGRAM.items():
            dtime = data['dtime']
            if dtime < since:
                self.remove_variogram(h)

    def _check_old_kriging(self, since_hours=1):
        # create the timestamp
        since = dt.utcnow() - td(hours=since_hours)

        # remove everything older than since
        for h, data in self.KRIGING.items():
            dtime = data['dtime']
            if dtime < since:
                self.remove_kriging(h)

    def __create_dataset(self, func, *args, **kwargs):
        # run the dataset creator
        result_dict = func(*args, **kwargs)

        # hash the result
        h = hashlib.sha256(str(result_dict).encode()).hexdigest()

        return h, result_dict

# instantiate a DataManager
DATAMANAGER = DataManager()
