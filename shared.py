import keras

model1: keras = keras.models.load_model("policy_black.h5")
model2: keras = keras.models.load_model("policy_white.h5")


EMPTY = 0
BLACK = 1
WHITE = 2