import sys
import torch
import chess
import time
import re
from boardtotensor import board_to_tensor

#Open the data

def pgn_eval_tensor(pgn_eval):
    #The final tensor with all the board positions
    final_position = None

    #the final eval tensor
    final_eval = None

    #Intialize a chess board on which the moves are played.
    board = chess.Board()
    #regex explanation (see "https://docs.python.org/3/library/re.html" for more detailed information):
    #(?<=...) matches the following expression if it is preceeded by ... (positive lookbehind assertion)
    #\s is a space character
    #[...] matches every character in ...
    #. matches any character except for a newline
    #*? is a non-greedy match: e.g. A.*B matches ABACB for the input ABACB, whereas
    #A.*?B results in two matches AB and ACB.
    #(?=...) matches the preceeding expression if it is followed by ... (lookahead assertion)
    #Moves in the file are of the following form:" square[\s?!#]" or " Piece+Square[\s?!#]", so we find them by looking for a
    move_lst = re.findall("(?<=\s)[a-hBKNOQR].*?(?=[\s?!#])", pgn_eval)
    #Evaluations are of the form: "eval number]" or " eval #number" or " move#"
    eval_lst = re.findall("(?<=l\s).*?(?=\])|#(?=\s)", pgn_eval)
    #Who is allowed to move (1 = white, -1 = white)
    who_move = 1

    #Initialize the Tensor of who moves [1,0] = white, [0,1] = black
    #They are appended to the board position tensor
    whitemove = torch.tensor([1,0])
    blackmove = torch.tensor([0,1])

    #Iterate through the moves, convert the position into a tensor and
    #concatenate them one after another
    for move in move_lst:

        #Make the move
        board.push_san(move)
        who_move *= -1

        #Convert the board to a tensor
        position = board_to_tensor(board)

        #If it is the first position set final_position = position, else concatenate with
        #final_position
        if final_position == None:
            position = torch.unsqueeze(position, 0)
            final_position = position

        else:
            position = torch.unsqueeze(position, 0)
            final_position = torch.cat((final_position, position), 0)

    #create the eval_tensor
    for evaluation in range(0,len(eval_lst)):

        #If the eval is checkmate we have to convert the checkmate eval to -1 or 1
        if eval_lst[evaluation][0] == "#":
            if len(eval_lst[evaluation]) == 1:
                if eval_lst[evaluation - 1][0] == "-":
                    eval_lst[evaluation] = "-15"
                else:
                    eval_lst[evaluation] = "15"

            elif eval_lst[evaluation][1] == "-":
                eval_lst[evaluation] = "-15"

            else:
                eval_lst[evaluation] = "15"

    #convert to float list
    eval_lst = [float(x) for x in eval_lst]

    #Normalize the data
    for evaluation in range(0,len(eval_lst)):
        #Values between -15 and 15 will be normalized by dividing by 15
        if -15.0 <= eval_lst[evaluation] < 15.0:
            eval_lst[evaluation] = eval_lst[evaluation]/15

        #Values outside of the interval [-15,15] will be normalized to -1 or 1, since they are
        #probably really close to a checkmate.
        else:
            eval_lst[evaluation] = eval_lst[evaluation]/abs(eval_lst[evaluation])

    #Convert to pytorch tensor
    final_eval = torch.tensor(eval_lst)

    #If final_eval.size(0) is not equal to final_position.size(0)
    #something went wrong and we discard the game.

    if final_position.size(0) != final_eval.size(0):
        return None, None



    return final_position, final_eval


#This function returns two different tensors: "a: Batch Dimension x BoardPositions" and "b: Batch Dimension x Evaluation
#of position"
#"end-start" has to be a multiple of 50000, by means of speeding up
def load_data(start, end, file):
    try:
        data = open(file, "r")

    except:
        print("Dateizugriff nicht erfolgreich.")
        sys.exit(0)

    lines = [next(data) for x in range(start,end)]
   
    #Initialize the final tensors
    train_tensor = None
    eval_tensor = None
    train_tensor_middle = None
    eval_tensor_middle = None
    #Iterate through the lines to only extract the lines
    #which contain a game. Lines which contain games start with
    #"1." or simply "1"
    counter = 0
    timer = time.time()

    for line in lines[start:end]:

        #This counter counts the lines
        counter += 1
        if counter % 50000 == 0 or counter == end:
                print(format((time.time() - timer)//60, '.0f'), "min:", format((time.time() - timer)%60, '.3f'), "sec for", counter, "lines.")
                if train_tensor == None:
                    train_tensor = train_tensor_middle
                    eval_tensor = eval_tensor_middle
                else:
                    train_tensor = torch.cat((train_tensor, train_tensor_middle), 0)
                    eval_tensor = torch.cat((eval_tensor, eval_tensor_middle), 0)

                train_tensor_middle = None
                eval_tensor_middle = None

        if line[0] == "1":
            #We have to check if the game is evaluated or not.
            #Evaluations are in curly braces "{}"
            for i in range(0,len(line)):
                if line[i] == "{":
                    #The game is evaluated and we now need to extract it
                    data, labels = pgn_eval_tensor(line)

                    #If the extraction was successful
                    if data != None:
                        if train_tensor_middle == None and eval_tensor_middle == None:
                            train_tensor_middle = data
                            eval_tensor_middle = labels

                        else:
                            train_tensor_middle = torch.cat((train_tensor_middle, data), 0)
                            eval_tensor_middle = torch.cat((eval_tensor_middle, labels), 0)

                        #After we extracted the game, we break the for loop
                        break

                #If we don't encounter a "{" but a "2" first, the game has
                #no evaluation and we can break the for loop to look for the
                #next game
                elif line[i] == "2":
                    break

        else:
            continue



    #Add batch-dimension to eval tensor
    if eval_tensor != None:
        eval_tensor = torch.unsqueeze(eval_tensor, 1)

    return train_tensor, eval_tensor
