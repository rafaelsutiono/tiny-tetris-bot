# import discord.py, RNG, and asyncio for running coroutines (lines of code that act on the occurence of an event loop)
import discord
from discord.ext import commands
import random
import asyncio

# for storing bot token
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# represents the game board as a 2d list
board = []
no_of_rows = 18 # represents rows
no_of_cols = 10 # represents columns

# emoji strings in discord to represent differently coloured pieces in tetris
empty_sq = ':black_large_square:'
blue_sq = ':blue_square:'
brown_sq = ':brown_square:'
orange_sq = ':orange_square:'
yellow_sq = ':yellow_square:'
green_sq = ':green_square:'
purple_sq = ':purple_square:'
red_sq = ':red_square:'

embed_colour = 0x00a36c # colour of line on embeds

# stores players' scores and number of lines cleared
points = 0
lines = 0

# tracks user input
down_pressed = False 
rotate_clockwise = False

rotation_pos = 0 # angle of rotation of a piece is defaulted to 0
h_movement = 0 # amount to move left or right
is_new_shape = False # tracks whether a new tetris piece has been placed on the board
start_higher = False # used when tetris piece is near the top of the board
game_over = False # keeps the game running, game stops if set to True
index = 0


class TetrisPieces: # represents tetris pieces
    # called when a new piece, i.e. instance, is created
    def __init__(self, starting_pos, colour, rotation_points):
        self.starting_pos = starting_pos # list that represents the starting position of the piece on the game board
        self.colour = colour # represents the color of the piece
        self.rotation_points = rotation_points # list of lists that stores data for rotating the tetris piece

main_wall_kicks = [ # stores data for rotating the J, L, T, S, and Z tetris pieces
                    [[0, 0], [0, -1], [-1, -1], [2, 0], [2, -1]],
                    [[0, 0], [0, 1], [1, 1], [-2, 0], [-2, 1]],
                    [[0, 0], [0, 1], [-1, 1], [2, 0], [2, 1]],
                    [[0, 0], [0, -1], [1, -1], [-2, 0], [-2, -1]]
                    ]

i_wall_kicks = [ # stores data for rotating the I tetris piece
                [[0, 0], [0, -2], [0, 1], [1, -2], [-2, 1]],
                [[0, 0], [0, -1], [0, 2], [-2, -1], [1, 2]],
                [[0, 0], [0, 2], [0, -1], [-1, 2], [2, -1]],
                [[0, 0], [0, 1], [0, -2], [2, 1], [-1, -2]]
                ]

rot_adjustments = { # a dictionary to store data for adjusting tetris piece positions after rotations
                # blue: no adjustment needed
                ':blue_square:': [[0, 1], [-1, -1], [0, 0], [-1, 0]], #[[0, 0], [0, 0], [0, 0], [0, 0]]
                # brown: left 1, right 1, right 1, left 1,
                ':brown_square:': [[0, 0], [0, 1], [0, 0], [0, -1]], #[[0, -1], [0, 1], [0, 1], [0, -1]]'
                # orange: left 1, nothing, right 1, nothing
                ':orange_square:': [[0, -1], [0, 0], [-1, 1], [0, 0]], #[[0, -1], [0, 0], [0, 1], [0, 0]]
                # yellow: no adjustment needed
                ':yellow_square:': [[0, 0], [0, 0], [0, 0], [0, 0]],
                # green: right 1, nothing, right 1, nothing
                ':green_square:': [[0, 0], [0, 0], [0, 0], [0, 0]], #[[0, 1], [0, 0], [0, 1], [0, 0]]
                # purple: nothing, right 1, left 1, right 1
                ':purple_square:': [[0, 0], [1, 1], [0, -1], [0, 1]], #[[0, 0], [0, 1], [0, -1], [0, 1]]
                #red: left 1, up 1, right 1, up 1
                ':red_square:': [[1, -1], [-1, -1], [0, 2], [-1, -1]] #[[0, -1], [-1, 0], [0, 1], [-1, 0]]
                }

# starting positions for each tetris piece, followed by their assigned colour and rotation points
shape_I = TetrisPieces([[0, 3], [0, 4], [0, 5], [0, 6]], blue_sq, [1, 1, 1, 1])
shape_J = TetrisPieces([[0, 3], [0, 4], [0, 5], [-1, 3]], brown_sq, [1, 1, 2, 2])
shape_L = TetrisPieces([[0, 3], [0, 4], [0, 5], [-1, 5]], orange_sq, [1, 2, 2, 1])
shape_O = TetrisPieces([[0, 4], [0, 5], [-1, 4], [-1, 5]], yellow_sq, [1, 1, 1, 1])
shape_S = TetrisPieces([[0, 3], [0, 4], [-1, 4], [-1, 5]], green_sq, [2, 2, 2, 2])
shape_T = TetrisPieces([[0, 3], [0, 4], [0, 5], [-1, 4]], purple_sq, [1, 1, 3, 0])
shape_Z = TetrisPieces([[0, 4], [0, 5], [-1, 3], [-1, 4]], red_sq, [0, 1, 0, 2])


#fill board with empty squares
def make_empty_board():
    for row in range(no_of_rows):
        # add a new empty row to the game board
        board.append([])
        for col in range(no_of_cols):
            # add an empty square to the current row of the game board
            board[row].append(empty_sq)

# fill the game board with a given emoji (the emojis are the coloured squares). This function will be used to fill the board with empty squares, i.e. black squares.
def fill_board(emoji):
    for row in range(no_of_rows):
        for col in range(no_of_cols):
            # checks whether the square is already filled with the given emoji string. If the square is not already filled with the given emoji string, the function replaces the square with the given emoji string
            if board[row][col] != emoji:
                board[row][col] = emoji

# format the game board as a string representation with newline characters (line breakers) at the end of each row, allowing the board to be displayed to the user
def format_board_as_str():
    # create an empty string that will hold the string representation of the game board, which then iterates over the rows and columns of the board using the following 'for' loops
    board_as_str = ''
    for row in range(no_of_rows):
        for col in range(no_of_cols):
            # adds emojis for each square to the string representation of the game board
            board_as_str += (board[row][col])
            # Add a newline character after the last square in the row
            if col == no_of_cols - 1:
                board_as_str += "\n "
    # return the string representation of the game board
    return board_as_str

# generates a random tetris piece for the game
def get_random_shape():
    global index
    shapes = [shape_I, shape_J, shape_L, shape_O, shape_S, shape_T, shape_Z]
    # set random_shape as a random shape object from the above list, which is done by generating a random integer between 0 and 6.
    random_shape = shapes[random.randint(0, 6)]
    index += 1
    # if start_higher is True, the function iterates over the starting_pos attribute of the random_shape object and subtracts 1 from the row value of each square in the attribute
    # this effectively moves the tetris piece up one row on the game board
    if start_higher == True:
        for s in random_shape.starting_pos[:]:
            s[0] = s[0] - 1
    else:
        # if start_higher is False, the function initializes a variable called starting_pos and sets it equal to a copy of the starting_pos attribute of the random_shape object.
        starting_pos = random_shape.starting_pos[:]
    random_shape = [random_shape.starting_pos[:], random_shape.colour, random_shape.rotation_points] #gets starting point of shapes and copies, doesn't change them
    global is_new_shape
    is_new_shape = True
    # returns random_shape as a list containing starting_pos, colour, and rotation_points attributes
    # effectively allowing the game to track the position, colour, and rotation data of the randomly generated tetris piece.
    return random_shape

def rotate_shape(shape, direction, rotation_point_index, shape_colour):
    rotation_point = shape[rotation_point_index] # assigns the value of the square at the rotation_point_index of the shape variable to the rotation_point variable
    new_shape = [] # to store coords of rotated shape

    for square in shape:
        # assign the value of the first and second element of the square to square_row and square_col respectively
        square_row = square[0]
        square_col = square[1]
        # check if direction is clockwise
        if direction == 'clockwise':
            # calculate the new positions of the square after a clockwise rotation
            new_square_row = (square_col - rotation_point[1]) + rotation_point[0] + rot_adjustments.get(shape_colour)[rotation_pos-1][0]
            print('Adjustment made: ' + str(rot_adjustments.get(shape_colour)[rotation_pos-1][0]))
            new_square_col = -(square_row - rotation_point[0]) + rotation_point[1] + rot_adjustments.get(shape_colour)[rotation_pos-1][1]
            print('Adjustment made: ' + str(rot_adjustments.get(shape_colour)[rotation_pos-1][1]))
        new_shape.append([new_square_row, new_square_col]) # store position of rotated square
        if (0 <= square_col < no_of_cols) and (0 <= square_row < no_of_rows): # check if the new square is within the game board
            board[square_row][square_col] = empty_sq # make the square at the old position empty on the game board

    new_shape = do_wall_kicks(new_shape, shape, shape_colour, 0) # call do_wall_kicks to offset shape

    new_shape = sorted(new_shape, key=lambda l:l[0], reverse=True) # sorts the new_shape list so that the bottom squares are first in the list
    print('Rotated shape: ' + str(new_shape))

    # place rotated shape (in case can't move down)
    if new_shape != shape:
        for square in new_shape:
            square_row = square[0]
            square_col = square[1]
            board[square_row][square_col] = shape_colour

    return new_shape

# handles 'wall kicks', i.e. adjustments made to the position of a tetris piece after it has been rotated
# wall kicks are necessary to ensure that a tetris piece doesn't get stuck against the wall or another piece after it has been rotated
def do_wall_kicks(shape, old_shape_pos, shape_colour, attempt_kick_num):
    new_shape_pos = []

    # determine which set of wall kick to use based on shape colour
    if shape_colour == blue_sq:
        kick_set = main_wall_kicks[rotation_pos]
    else:
        kick_set = i_wall_kicks[rotation_pos]

    print('Kick set: ' + str(kick_set))
    for kick in kick_set:
        print('Kick: ' + str(kick))
        for square in shape:
            # assign the value of the first and second element of the square to square_row and square_col respectively
            square_row = square[0]
            square_col = square[1]
            # assign the value of square_row plus the value of the first element of kick to new_square_row and square_col plus the value of the second element of kick to new_square_col
            new_square_row = square_row + kick[0]
            new_square_col = square_col + kick[1]
            if (0 <= new_square_col < no_of_cols) and (0 <= new_square_row < no_of_rows): # check if the new square is within the game board
                square_checking = board[new_square_row][new_square_col] # get the square to check if empty
                if (square_checking != empty_sq) and ([new_square_row, new_square_col] not in old_shape_pos): # if square is not empty / won't be when other parts of shape have moved
                    # shape doesn't fit
                    new_shape_pos = [] #reset new_shape
                    break
                else: # shape does fit
                    new_shape_pos.append([new_square_row, new_square_col]) # store new position
                    print('New shape: ' + str(new_shape_pos))
                    if len(new_shape_pos) == 4:
                        print('Returned new shape after doing kicks')
                        return new_shape_pos # return shape with kicks added
            else:
                # shape doesn't fit
                new_shape_pos = [] # reset new_shape
                break

    print('Returned old, unrotated shape')
    return old_shape_pos # return shape without rotation

def clear_lines():
    # make the board, points and lines variables global, so that the function can modify their values
    global board
    global points
    global lines
    lines_to_clear = 0
    for row in range(no_of_rows):
        row_full = True # assume line is full
        for col in range(no_of_cols):
            if board[row][col] == empty_sq:
                row_full = False
                break # exit nested loop if the current square is empty
        if row_full:
            lines_to_clear += 1
            board2 = board[:] # create a copy of the board variable
            for r in range(row, 0, -1): # nested loop that iterates over each row above the current row from the bottom to the top
                if r == 0: # check if current row is the top row
                    for c in range(no_of_cols): # nested loop that iterates over each column of the top row
                        board2[r][c] = empty_sq # make the current square of the top row empty
                else:
                    for c in range(no_of_cols):
                        board2[r][c] = board[r - 1][c] # make the current square of the current row the same as the one above it
            board = board2[:] # make the board variable equal to the modified board2 variable
    # scoring system
    if lines_to_clear == 1:
        points += 100
        lines += 1
    elif lines_to_clear == 2:
        points += 300
        lines += 2
    elif lines_to_clear == 3:
        points += 500
        lines += 3
    elif lines_to_clear == 4:
        points += 800
        lines += 4

# check if the next position for the current shape is available
# takes in one argument, cur_shape_pos, which is the current position of the shape on the board
def get_next_pos(cur_shape_pos):
    global h_movement
    global start_higher
    global game_over

    # initialize the amount of movement that the shape should move to
    movement_amnt = 1

    if down_pressed == False:
        amnt_to_check = 1 # assign amnt_to_check variable as 1, which means that the function will check the space one below the current shape
    else:
        amnt_to_check = no_of_rows # amnt_to_check is assigned as no_of_rows, which means that the function will check all the rows until the furthest available space

    for i in range(amnt_to_check):
        square_no_in_shape = -1
        for square in cur_shape_pos:
            # check if the next position for the square is on the board and if the next position is empty
            # if not empty, it checks if the shape can fit there. If not, it sets next_space_free as false, and if it is a new shape and start_higher is true, it sets game_over as true
            next_space_free = True
            square_no_in_shape += 1
            square_row = square[0]
            square_col = square[1]
            if (0 <= square_col < no_of_cols): # if current column spot will fit
                if not (0 <= square_col + h_movement < no_of_cols): # if spot with column position changed won't fit
                    h_movement = 0
                if (0 <= square_row + movement_amnt < no_of_rows): # if new square row pos is on board
                    square_checking = board[square_row + movement_amnt][square_col + h_movement] # get the square to check if empty
                    if (square_checking != empty_sq) and ([square_row + movement_amnt, square_col + h_movement] not in cur_shape_pos): # if square is not empty / won't be when other parts of the shape have moved
                        # check if space is free if not moving horizontally, but is still going down
                        h_movement = 0
                        square_checking = board[square_row + movement_amnt][square_col + h_movement]
                        if (square_checking != empty_sq) and ([square_row + movement_amnt, square_col + h_movement] not in cur_shape_pos):
                            if movement_amnt == 1:
                                next_space_free = False # can't put shape there
                                print('Detected a space that isnt free')
                                print('Square checking: ' + str(square_row + movement_amnt) + ', ' + str(square_col + h_movement))
                                if is_new_shape: # if can't place new shape
                                    if start_higher == True:
                                        game_over = True
                                    else:
                                        start_higher = True
                            elif movement_amnt > 1:
                                movement_amnt -= 1 # accomodate for extra 1 added to check if it's free
                            return [movement_amnt, next_space_free]
                    elif down_pressed == True:
                        if square_no_in_shape == 3: # only on last square in shape
                            movement_amnt += 1 # increase amount to move shape by
                elif square_row + movement_amnt >= no_of_rows:
                    if movement_amnt == 1:
                        next_space_free = False # can't put shape there
                        print('Detected a space that isnt free')
                    elif movement_amnt > 1: 
                        movement_amnt -= 1 # accomodate for extra 1 added to check if it's free
                    return [movement_amnt, next_space_free]
                elif down_pressed == True:
                    if square_no_in_shape == 3: # only on last square in shape
                        movement_amnt += 1 # increase amount to move shape by

    return [movement_amnt, next_space_free]


async def run_game(msg, cur_shape):
    global is_new_shape
    global h_movement
    global rotate_clockwise
    global rotation_pos

    cur_shape_pos = cur_shape[0] # assign the value of the first element of the cur_shape list to the variable cur_shape_pos
    cur_shape_colour = cur_shape[1] # assign the value of the second element of the cur_shape list to the variable cur_shape_colour

    # checks if the variable rotate_clockwise is equal to True and the variable cur_shape_colour is not equal to the variable yellow_sq
    if rotate_clockwise == True and cur_shape_colour != yellow_sq:
        cur_shape_pos = rotate_shape(cur_shape_pos, 'clockwise', cur_shape[2][rotation_pos], cur_shape_colour) # rotate shape
        cur_shape = [cur_shape_pos, cur_shape_colour, cur_shape[2]] # update shape

    next_pos = get_next_pos(cur_shape_pos)[:]
    movement_amnt = next_pos[0]
    next_space_free = next_pos[1]

    # move/place shape if position is available
    square_no_in_shape = -1
    # if the next position for the shape is free (determined in the previous function get_next_pos), the code enters a loop that iterates through each square in the current shape's position
    if next_space_free:
        for square in cur_shape_pos:
            square_no_in_shape += 1 # for each square, square_no_in_shape is incremented by 1, and the row and column of the square are stored in square_row and square_col respectively
            square_row = square[0]
            square_col = square[1]
            if (0 <= square_row + movement_amnt < no_of_rows): # if new square row pos is on board
                square_changing = board[square_row + movement_amnt][square_col + h_movement] # get square to change
                board[square_row + movement_amnt][square_col + h_movement] = cur_shape_colour # changes square colour to colour of shape
                if is_new_shape == True:
                    is_new_shape = False # has been placed, so not new anymore
                if square_row > -1: # stops from wrapping around list and changing colour of bottom rows
                    board[square_row][square_col] = empty_sq # make old square empty again
                cur_shape_pos[square_no_in_shape] = [square_row + movement_amnt, square_col + h_movement]
            else: # if new square row position is not on the board
                cur_shape_pos[square_no_in_shape] = [square_row + movement_amnt, square_col + h_movement]
    else:
        global down_pressed
        down_pressed = False
        clear_lines() # check for full lines and clear them
        cur_shape = get_random_shape() # change shape
        rotation_pos = 0 # reset rotation
        print('Changed shape.')

    if not game_over:
        # update board
        embed = discord.Embed(description=format_board_as_str(), color=embed_colour)
        h_movement = 0 # reset horizontal movement
        rotate_clockwise = False # reset clockwise rotation
        await msg.edit(embed=embed)
        if not is_new_shape:
            await asyncio.sleep(1) # to keep under discord's API rate limit
        await run_game(msg, cur_shape)
    else:
        print('GAME OVER')
        desc = 'Score: {} \n Lines: {} \n \n Press ▶ to play again.'.format(points, lines)
        embed = discord.Embed(title='GAME OVER', description=desc, color=embed_colour)
        await msg.edit(embed=embed)
        await msg.remove_reaction("⬅", client.user) # Left
        await msg.remove_reaction("⬇", client.user) # Down
        await msg.remove_reaction("➡", client.user) # Right
        await msg.remove_reaction("🔃", client.user) # Rotate
        await msg.add_reaction("▶") # Play

# reset the game to its initial state
async def reset_game():
    global down_pressed
    global rotate_clockwise
    global rotation_pos
    global h_movement
    global is_new_shape
    global start_higher
    global game_over
    global points
    global lines
    fill_board(empty_sq) # fill the game board with empty squares
    down_pressed = False
    rotate_clockwise = False
    rotation_pos = 0
    h_movement = 0
    is_new_shape = False
    start_higher = False
    game_over = False
    next_space_free = True
    points = 0
    lines = 0

make_empty_board()


#-------------------------------------------------------------------------------

# sets up the bot
client = commands.Bot(command_prefix = 't.',intents=discord.Intents().all()) # prefix set to 't.', all intents enabled

# triggers if bot logs in
@client.event
async def on_ready():
    print("logged in :D")

@client.command()
async def start(ctx): # create an initial game board and sends an embed message with the game board and instructions on how to play. It also adds the "▶" reaction to the message, which allows the user to start the game
    await reset_game()
    embed = discord.Embed(title='Tiny Tetris Bot', description=format_board_as_str(), color=embed_colour)
    embed.add_field(name='How to Play:', value='Use ⬅ ⬇ ➡ to move left, down, and right respectively. \n  \n Use 🔃 to rotate the shape clockwise. \n \n Press ▶ to Play.', inline=False)

    msg = await ctx.send(embed=embed)

    # add button choices / reactions
    await msg.add_reaction("▶") # Play

@client.event
# triggered whenever a user adds a reaction to a message
# checks the reaction emoji and performs the corresponding action such as move left, right, down, rotate, stop the game or delete the game board
async def on_reaction_add(reaction, user):
    global h_movement
    global rotation_pos
    if user != client.user:
        msg = reaction.message
        if str(reaction.emoji) == "▶": # Play button pressed
            print('User pressed play')
            await reset_game()
            await msg.remove_reaction("❌", client.user) # remove Delete
            embed = discord.Embed(description=format_board_as_str(), color=embed_colour)
            await msg.remove_reaction("▶", user)
            await msg.remove_reaction("▶", client.user)
            await msg.edit(embed=embed)
            await msg.add_reaction("⬅") # Left
            await msg.add_reaction("⬇") # Down
            await msg.add_reaction("➡") # Right
            await msg.add_reaction("🔃") # Rotate
            await msg.add_reaction("❌") # Stop Game
            starting_shape = get_random_shape()
            await run_game(msg, starting_shape)

        if str(reaction.emoji) == "⬅": # Left button pressed
            print('Left button pressed')
            h_movement = -1 # move 1 left
            await msg.remove_reaction("⬅", user)
        if str(reaction.emoji) == "➡": # Right button pressed
            print('Right button pressed')
            h_movement = 1 # move 1 right
            await msg.remove_reaction("➡", user)
        if str(reaction.emoji) == "⬇": # Down button pressed
            print('Down button pressed')
            global down_pressed
            down_pressed = True
            await msg.remove_reaction("⬇", user)
        if str(reaction.emoji) == "🔃": # Rotate button pressed
            print('Rotate clockwise button pressed')
            global rotate_clockwise
            rotate_clockwise = True
            if rotation_pos < 3:
                rotation_pos += 1
            else:
                rotation_pos = 0 # go back to original position
            await msg.remove_reaction("🔃", user)
        if str(reaction.emoji) == "❌": # Stop game button pressed
            await reset_game()
            await msg.delete()
        if str(reaction.emoji) == "🔴":
            await msg.edit(content="")


client.run(TOKEN)