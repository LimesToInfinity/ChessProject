A neuralnetwork that plays chess.

## The different files

### alphabeta.py
#### alpha_beta()
This file contains the alpha-beta pruning algorithm, which is used to search within the game tree.
One can use the alpha-beta pruning algorithm by calling the function alpha_beta() from within this module.
The function alpha_beta() is kept general to be reused by different games, not just chess.
alpha_beta(game, turn, depth=1) receives 3 arguments:
1. game: The current state of the board 
2. turn: Who's turn is it?
3. depth: How deep should the algorithm search?

For chess purposes we use the python-chess library (see https://python-chess.readthedocs.io/en/latest/index.html).
We are using the chess.Board() class to represent our chess board. This class comes with convenient features to alter the board position, such as
board.push(move) which makes a move and board.pop() which undoes the last move.  
By default we hand over a chess.Board() object as the game argument for alphabeta().  
The turn argument is a boolean value, "White"=True, "Black"=False, or more general Maximizing player=True and Minimizing player=False.  
The depth argument is 1 by default, but can be any positive integer value.

#### make_move()
This function makes a move on the board. If you want to use the alpha-beta pruning algorithm for a different purpose than chess, you have to change this.

#### take_back_move()
Undoes the last move on the board. If you want to use the alpha-beta pruning algorithm for a different purpose than chess, you have to change this.

#### checkmate_stalemate()
Checks if the current position is a checkmate and returns the evaluation 1.1 (win) or stalemate 0 (draw). If you want to use the alpha-beta pruning algorithm for a different purpose than chess, you have to change this.

#### maximal() & minimal()
These are the functions which calculate the alpha/beta values for a given game tree branche. They return the alpha/beta value and best_move for the player who minimizes (black) or the player
who maximizes (white).

------------------------------------
### boardtotensor.py
This file contains the function
#### board_to_tensor():
It takes in a chess.Board() object and returns a PyTorch tensor of size (386). It first creates a tensor of size (64,6) which encodes the chess board with all it's pieces.
  
After the chess board is encoded we flatten the torch tensor and concatenate it with a pytorch tensor [1,0] or [0,1] (white or black) to add information about which side moves in the current position.  
This is important for the neural network since the evaluation of a position depends upon which side moves next.

------------------------------------
### neuralnetwork.py
This file contains the following functions:
#### NeuralNet()
This function receives 1 argument, the depth of the neural network, which can be an integer bigger or equal to 2.  
It then creates a PyTorch Sequential Model with the following structure:  
Linear(386,500) -> Tanh activation -> [(Linear(500,500) -> Tanh)*depth-2] -> Linear(500,1) -> Tanh activation.  
The function than returns the Sequential Model, the optimizer which is set to SGD=Stochastic Gradient Descent and the loss_fn which is set to MSELoss=Mean Squared Error loss

#### training_loop()
training_loop(n_epochs, model, loss_fn, optimizer) receives the number of training epochs=n_epochs, the Sequential Model=model, the loss function=loss_fn and the optimizer=optimizer.  
The train and label tensors are preloaded inside of neuralnetowork.py and are called train.pt and label.pt, which is important if you create your own ones. 
With these parameters it trains the Sequential model.

-----------------------------------
### ordering.py
This file contains the function 
#### ordering_moves()
which orders the moves for improved alpha-beta pruning performance.
It orders in the following hirachy: 1. checks, 2. captures, 3. castling, 4. anything else.

----------------------------------
### ratingmodel.py
This file contains the function
#### rating_model()
which receives a model (neural net) and a game position (chess.Board - object) and outputs an evaluation of the position in the interval [-1,1].
