import numpy as np


def data(data_id: int) -> np.ndarray:
    np.random.seed(4242)
    if data_id == 0:
        local_data = np.random.normal(50.0, 15.0, size=1000)
    if data_id == 1:
        local_data = np.random.normal(90.0, 15.0, size=1000)
    return local_data
