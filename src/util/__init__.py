"""
La ou ya des utilitaires (log, math, etc) merci copilot
"""

import numpy as np

type array_type = np.ndarray[tuple[int, ...], np.dtype[np.floating]]


class MetaSingleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

