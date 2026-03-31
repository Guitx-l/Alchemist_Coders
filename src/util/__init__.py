"""
La ou ya des utilitaires (log, math, etc) merci copilot
"""

from typing import Callable
import numpy as np
import rsk

type array_type = np.ndarray[tuple[int, ...], np.dtype[np.floating]]
type update_function_type = Callable[[rsk.Client, str, int, int, array_type, dict], None]

