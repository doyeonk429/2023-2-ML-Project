import keras.backend as K
from numpy import ndarray



def reshape_to_15_15_1(data: ndarray):
    return K.reshape(data, [-1, 15, 15, 1])

def change_color(color: int):
    if color == 1:
        return 2
    else:
        return 1

