import torch
import chess

#Used to convert the board (which is represented as a Chess Board object) to a 64x6 pytorch tensor.
#We need 6 columns for the 6 different pieces (King, Queen, Bishop, Knight, Rook, Pawn) which could
#be present on a square. We will represent a white/black piece on a certain square as 1/-1 in the tensor.
#The 6 columns represent the pieces in the following index ascending order: Pawn, Knight, Bishop, Queen, King

def board_to_tensor(board):
    board_tensor = torch.zeros((64,6))
    for i in range(0,64):
        #Gets the piece on sqare i with 0-a1, 1-b1, 2-c1, ... , 62-g8, 63-h8
        piece = board.piece_at(i)
        
        #If square is empty None is returned
        if piece != None:
            
            #Gets the piece symbol: lower case for black, upper case for white
            piece = piece.symbol()
            
            #Depending on the piece type, choose one of the Square states (1 for white pieces, -1 for black pieces) 
            if piece == "P":
                board_tensor[i,0] = 1

            elif piece == "N":
                board_tensor[i,1] = 1

            elif piece == "B":
                board_tensor[i,2] = 1

            elif piece == "R":
                board_tensor[i,3] = 1

            elif piece == "Q":
                board_tensor[i,4] = 1

            elif piece == "K":
                board_tensor[i,5] = 1

            elif piece == "p":
                board_tensor[i,0] = -1

            elif piece == "n":
                board_tensor[i,1] = -1

            elif piece == "b":
                board_tensor[i,2] = -1

            elif piece == "r":
                board_tensor[i,3] = -1

            elif piece == "q":
                board_tensor[i,4] = -1

            elif piece == "k":
                board_tensor[i,5] = -1
    
    
    #Flatten the tensor, so it's one dimensional, and we can feed it to the neural net later
    board_tensor = torch.flatten(board_tensor)
    if board.turn:
        board_tensor = torch.cat((board_tensor, torch.tensor([1.0, 0.0])),0)
    else:
        board_tensor = torch.cat((board_tensor, torch.tensor([0.0, 1.0])),0)
    
    return board_tensor
