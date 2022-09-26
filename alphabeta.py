import torch
import time
import chess
from boardtotensor import board_to_tensor
from ordering import ordering_moves
from ratingmodel import rating_model

#--------------------------------------------------------------------
#Load the A.I.
model = torch.load("./Chess_Rating_Model")
for p in model.parameters():
    p.requires_grad = False
#--------------------------------------------------------------------
def make_move(game, move):
    game.push(move)

#--------------------------------------------------------------------
def take_back_move(game):
    game.pop()

#--------------------------------------------------------------------
def checkmate_stalemate(game):
    if game.is_checkmate():
        return 1.1
    
    #If there are no legal moves and the position is not checkmate, it's a stalemate
    else:
        return 0

#--------------------------------------------------------------------
def maximal(game, depth, alpha=-2, beta=2):
    
    #First we order the moves
    moves = ordering_moves(game)
    global total_leaves
    global visited_leaves
    best_move = None
    
    #Check for checkmate or stalemate
    if moves == []:
        alpha = checkmate_stalemate(game)
        alpha = alpha * (-1)
        return alpha, best_move

    #There are still legal moves to play
    else:
        #If depth==1 we rate the moves
        if depth==1:
            total_leaves += len(moves)
            for move in moves:
                visited_leaves += 1
                make_move(game, move)
                rating = rating_model(model, game)
                take_back_move(game)
                if alpha < rating:
                    alpha = rating
                    if beta > rating:
                        best_move = move
                    else:
                        #Beta-Cutoff
                        break

        #If depth is > 1 we have to climb further up the tree.
        else:
            for move in moves:
                make_move(game, move)
                rating,_ = minimal(game, depth-1, alpha=alpha, beta=2)
                take_back_move(game)
                if rating > alpha:
                    alpha = rating
                    if rating < beta:
                        best_move = move
                    else:
                        #Beta-Cutoff
                        break
        return alpha, best_move


#--------------------------------------------------------------------
def minimal(game, depth, alpha=-2, beta=2):

    #First we order the moves
    moves = ordering_moves(game)    
    global total_leaves
    global visited_leaves
    best_move = None
    
    #Check for checkmate or stalemate
    if moves == []:
        beta = checkmate_stalemate(gambe)
        beta = beta
        return beta, best_move
    
    #There are still legal moves
    else:
        #If depth == 1 we rate the moves
        if depth == 1:
            total_leaves += len(moves)
            for move in moves:
                visited_leaves += 1
                make_move(game, move)
                rating = rating_model(model, game)
                take_back_move(game)
                if rating < beta:
                    beta = rating
                    if rating > alpha:
                        best_move = move
                    else:
                        #Alpha-Cutoff
                        break

        #If depth is > 1 we have to climb further up the tree.
        else:
            for move in moves:
                make_move(game, move)
                rating,_ = maximal(game, depth-1, alpha=-2, beta=beta)
                take_back_move(game)
                if rating < beta:
                    beta = rating
                    if rating > alpha:
                        best_move = move

                    else:
                        #Alpha-Cutoff
                        break

        return beta, best_move


#--------------------------------------------------------------------
def alpha_beta(game, turn, depth=1):
    
    #Initialize the leave count
    global total_leaves
    global visited_leaves
    total_leaves = 0
    visited_leaves = 0
    timer = time.time()
    
    #The player who tries to maximize plays
    if turn:
        rating, best_move = maximal(game, depth, alpha=-2, beta=2)
        print("move:", best_move, "|rating:", format(float(rating), '.6f'), "|total_leaves:", total_leaves, "|visited leaves:", visited_leaves, "|time:", format((time.time()-timer)//60, '.0f'), "min:", format((time.time()-timer)%60, '.3f'), "sec")
        return best_move

    #The player who tries to minimize plays
    else:
        rating, best_move = minimal(game, depth, alpha=-2, beta=2)
        print("move:", best_move, "|rating:", format(float(rating), '.6f'), "|total_leaves:", total_leaves, "|visited leaves:", visited_leaves, "|time:", format((time.time()-timer)//60, '.0f'), "min:", format((time.time()-timer)%60, '.3f'), "sec")
        return best_move
