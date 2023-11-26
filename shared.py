import keras




MAX_ROLLOUT = 60
MAX_EXPAND_CHILDS = 30


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from mcts_module import MCTS

model1: keras = keras.models.load_model("policy_black.h5")
model2: keras = keras.models.load_model("policy_white.h5")
value_model: keras = keras.models.load_model("value_net.h5",compile=False)



mcts_tree : 'MCTS' = None


EMPTY = 0
BLACK = 1
WHITE = 2