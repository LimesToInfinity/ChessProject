import chess

def ordering_moves(game):
    ordered_moves = []
    check_moves = []
    capture_moves = []
    castling_moves = []
    move_list = list(game.legal_moves)
    
    for move in move_list:
        if game.gives_check(move):
            check_moves.append(move)
        elif game.is_capture(move):
            capture_moves.append(move)
        elif game.is_castling(move):
            castling_moves.append(move)
        
    ordered_moves = check_moves + capture_moves + castling_moves
    try:
        move_list.remove(ordered_moves)
    
    except:
        pass
    
    ordered_moves = ordered_moves + move_list
    
    return ordered_moves

