import chess #Would already be imported by boardtotensor
import torch #Would already be imported by boardtotensor
from boardtotensor import board_to_tensor


#This is the definition of our rating model, which evaluates a given position
def rating_model(model, game):
    tensor = board_to_tensor(game)
    prediction = model(tensor)
    return prediction
