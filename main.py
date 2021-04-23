import copy
import os
from termcolor import colored




class Board:
    '''
    Class that describe the current state of a board for Connect Four. We assume a 7x6 grid.
    '''
    def __init__(self, board=[[0,0,0,0,0,0,0] for i in range(6)]):
        self.board = board
    
    def __str__(self):
        new = []
        new.append("  1   2   3   4   5   6   7 \n")
        new.append("  -   -   -   -   -   -   - \n")

        for i in range(5,-1,-1): #print inverse order for visualizing correct board
            
            for j in range(7):
                if self.board[i][j] == 0: #empty place
                    new.append('| '+ '  ')
                elif self.board[i][j] == 1: #X
                    new.append('| ' + colored('X', 'red')+' ')
                elif self.board[i][j] == 2: #O
                    new.append('| ' + colored('O', 'blue')+' ')
                else:
                    print('deu ruim')
            new.append('|\t' + str(i+1) + ' '+ '\n')

        return ''.join(new)
    

def countSequences(board, n, player):
    '''Counts the number of n (being 2 or 3) sequences for a given board.
    Again I make the counts for a player (either 1/Xs being the real player or 2/Os being the AI)
    '''
    qt = 0
    #For each piece, see if one of these sequences start on that piece
    for i in range(6):
        for j in range(7):
            if board[i][j] != player:
                continue
            #Getting next n vertical positions
            vert = []
            for x in range(i+1, i+n):
                if x < 6:
                    vert.append(board[x][j])
                else:
                    vert = False
                    break
            
            #Getting next n horizontal positions
            horiz = []
            for y in range(j+1, j+n):
                if y < 7:
                    horiz.append(board[i][y])
                else:
                    horiz = False
                    break
                    
            #Getting next n diagonal positions
            diag = []
            t = 0
            while t < n:
                if (i+t) < 6 and (j+t) < 7:
                    diag.append(board[i+t][j+t])
                    t += 1
                else:
                    diag = False
                    break
                
            
            #getting next n negative diagonal positions
            neg_diag = []
            t = 0
            while t < n:
                if (i-t) >= 0 and (j+t) < 7:
                    neg_diag.append(board[i-t][j+t])
                    t += 1
                else:
                    neg_diag = False
                    break
            
            if vert:
                if len(set(vert)) == 1 and vert[0]==player:
                    qt += 1
            if horiz:
                if len(set(horiz)) == 1 and horiz[0]==player:
                    qt += 1
            
            if diag:
                if len(set(diag)) == 1 and diag[0]==player:
                    qt += 1
            
            if neg_diag:
                if len(set(neg_diag)) == 1 and neg_diag[0]==player:
                    qt += 1
    return qt
    
    

    
def getScore(board):
    '''
    Calculate the score for a given board configuration
    for a 7x6 grid in the form of arrays of arrays.
    In order to calculate the score, I am assuming the AI plays Os and
    the real player plays Xs. I also assume a high value means the AI Os 
    are closer to getting a sequence of 4, while a low value (very negative)
    means the real player is very close to getting a sequence of 4.
    
    To measure the actual score, I count the number of sequence of 2, 3 and 4 
    pieces and multiply the counts by 10 for 2 and 100 for 3. If there are 4 
    in a row, this means the game is over and therefore the score is plus or minus
    infinity. 
    '''
    AI3s = countSequences(board, 3, 2)#AI has value of 2 for player
    AI2s = countSequences(board, 2, 2)
    AI4s = countSequences(board, 4, 2)
    player3s = countSequences(board, 3, 1)#Real player has value of 1 for player
    player2s =countSequences(board, 2, 1)
    player4s = countSequences(board, 4, 1)
    
    if AI4s > 0:
        return float('inf')#AI won the game
    
    elif player4s > 0:
        return -float('inf')#Real player won
    
    else:
        return (100*AI3s + 10*AI2s - 100*player3s - 10*player2s) 
    

def getNextMoves(board, player):
    '''
    Given a current board configuration, get the next possible states
    by the current player being able to position the piece in any one of
    the 7 possible columns for a given player's turn (1 or 2)
    '''
    results = {}
    
    for j in range(7):
        if board[5][j] != 0:
            continue
        results[j] = copy.deepcopy(board)
    
    for j in range(7):
        #check if we can put a piece on this column
        if board[5][j] != 0:
            continue
        i = 0
        while board[i][j] != 0:
            i += 1#go up until you find the index of next free row
        #next state will now be putting a 'player' piece on position i,j
        results[j][i][j] = player
    return results.values() #return all possible new board configurations

def checkGameOver(board):
    '''
    Function to return boolean value on the game status: True is there is a 
    sequence of 4 pieces for either player.
    '''
    AI4s = countSequences(board, 4, 2)
    player4s = countSequences(board, 4, 1)
    if AI4s > 0 or player4s > 0:
        return True
    else:
        return False



def chooseAINextMove(board, depth):
    '''
    I am assuming its the AIs turn now, and I will calculate the utility score
    of each possible move by calling the miniMaxAlphaBeta as the real player's 
    next move for each candidate move and comparing the scores.
    '''
    nextMoveBoard = None
    currentMaxEval = -float('inf')
    alpha = -float('inf')
    beta = float('inf')
    next_moves = getNextMoves(board, 2)
    for child in next_moves:
        score = miniMaxAlphaBeta(child, depth-1, alpha, beta, False)#its the real player's move now
        if score > currentMaxEval:
            currentMaxEval = score
            nextMoveBoard = child
    return nextMoveBoard


def miniMaxAlphaBeta(board, depth, alpha, beta, maxplayer=True):
    '''
    Function to implement the minimax algorithm with alpha beta pruning. 
    Here I assume we are always maximizing for the AI player, represented by the integer 2(Os)
    '''
    game_over = checkGameOver(board)
    if depth == 0 or game_over:
        return getScore(board)
    if maxplayer: #currently the AIs turn to maximize score
        maxEval = -float('inf')
        next_moves = getNextMoves(board, 2)
        for child in next_moves:
            evl = miniMaxAlphaBeta(child, depth-1, alpha, beta, False)
            maxEval = max(maxEval, evl)
            alpha = max(alpha, evl)
            if beta <= alpha:
                break
        return maxEval
        
    else: #currently the real player's hypothetical turn to minimize score
        minEval = float('inf')
        next_moves = getNextMoves(board, 1)
        for child in next_moves:
            evl = miniMaxAlphaBeta(child, depth-1, alpha, beta, True)
            minEval = min(minEval, evl)
            beta = min(beta, evl)
            if beta <= alpha:
                break
        return minEval
    
#For a given board and depth as level of difficulty, simply call
#chooseAINextMove(board, depth)

#To get a real player's next move:

def boardFilled(board):
    '''
    Checking if there is any free spot (return board not filled)
    otherwise return true as in board is filled
    '''
    for i in board:
        for j in i:
            if j == 0:
                return False
    return True

def realPlayerMove(board, column):
    '''
    Given a real players choice of column to put their piece, make the move
    and return the new board
    '''
    if board[5][column] != 0:
        return False
    else:
        i = 0
        while board[i][column] != 0:
            i += 1
        board[i][column] = 1
        return board
    
def printBoard(board):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Board(board))
    

    
def checkWinner(board):
    '''
    Function to return boolean value on the game status: True is there is a 
    sequence of 4 pieces for either player.
    '''
    AI4s = countSequences(board, 4, 2)
    player4s = countSequences(board, 4, 1)
    if AI4s > 0 :
        return 'AI'
    elif player4s > 0:
        return 'Player'
    else:
        return False
    
def main():
    game_going = True
    print('Welcome to Connect 4! You will play with Xs')
    name = input('Whats your name?')
    whoStart = input('Do you want to start? (y/n)').lower()
    while whoStart != 'y' and whoStart != 'n':
        whoStart = input("Please enter a valid 'y' or 'n' to choose who starts").lower()
    dif = input('Choose a dificulty level from 1 to 5 (enter the digit only)')
    while not dif.isdigit():
        dif = input('Choose a valid difficulty level(1-5)')
    
    dif = int(dif)
    
    board = board=[[0,0,0,0,0,0,0] for i in range(6)]
    
    
    
    if whoStart == 'y':#real player first
        currentTurn = True
    else:
        currentTurn = False #AIs turn
    
    
    printBoard(board)
    print('Current Level: %d'%(dif))
    print('Player name:%s'%(name))
    #Game starts
    while(game_going):
        if boardFilled(board):
            print('GAME OVER')
            break
            
        if currentTurn: #Real Player's turn
            column = input("Choose a column from 1 to 7 to put your next X piece")
            while not column.isdigit():
                column = input('Choose a valid column')
            column = int(column) - 1
            new_board = realPlayerMove(board, column)
            while not board:#if cant choose that column
                column = input('Choose a valid column')
                column = int(column)
                new_board = realPlayerMove(board, column)
            board = new_board
            printBoard(board)
            print('Current Level: %d'%(dif))
            print('Player name:%s'%(name))

            win = checkWinner(board)
            if not win:
                currentTurn = False
                continue
            else:
                print('Winner is %s'%(win))
                break
        else: #AIs turn
            next_mv = chooseAINextMove(board, dif)
            if not next_mv: #means AI will lose because no optimal move
                next_board = list(getNextMoves(board, 2))[0]
                printBoard(next_board)
                print('Current Level: %d'%(dif))
                print('Player name:%s'%(name))
                print('Congrats, YOU WON %s!'%(name))
                break
            board = next_mv
            printBoard(board)
            print('Current Level: %d'%(dif))
            print('Player name:%s'%(name))
            win = checkWinner(board)
            if not win:
                currentTurn = True
                continue
            else:
                print('Winner is %s'%(win))
                break

if __name__ == "__main__":
    # execute only if run as a script
    main()
