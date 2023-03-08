import turtle
import math
import time
import random
import numpy as np

wn = turtle.Screen()
wn.bgcolor("papayawhip")
wn.title("A Maze Game")
wn.setup(1920,1080)

turtle.register_shape("tial.gif")
turtle.register_shape("tiar.gif")
turtle.register_shape("tia1l.gif")
turtle.register_shape("tia1r.gif")
turtle.register_shape("wall1.gif")
turtle.register_shape("wall2.gif")
turtle.register_shape("wall3.gif")
turtle.register_shape("wall4.gif")
turtle.register_shape("road.gif")
turtle.register_shape("pass.gif")
turtle.register_shape("pass1.gif")

MAZE_WIDTH = 25
MAZE_HEIGHT = 20
NUM_MOVES = 100
WINDOW_X = MAZE_WIDTH * 44
WINDOW_Y = MAZE_HEIGHT * 44 + 40
WHITE = (255, 255, 255)
TEXT_Y = WINDOW_Y - 30#WINDOW_Y * 23/24
TEXT_X = 110 #WINDOW_X/8
TEXT_SIZE = 16
FIT_FUNC = "distance" # "unique" or "distance"
NUM_PLAYERS = 20
MUTATION_RATE = 0.5
SELECTION_CUTOFF = 0.1
PLAYER_SPEED = 100 #num of pixels the player moves, leave it at 100
MOVE_OPTIONS = ["right", "left", "up", "down"]
DEAD_END_PENALTY = 200
MADEIT_THRESH = 0 # Put zero if only one duck will do
QUACKS_FILEPATH = "C:/Users/Justi/PycharmProjects/maze/duck_sounds"
GENERATION_THRESH = 50
FPS = 26
FOUND = False

# ********************************************************************
class Pen(turtle.Turtle):
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.shape("square")
        self.color("white")
        self.penup()
        self.speed(0)
        
class PassW(turtle.Turtle):
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.shape("pass1.gif")
        self.color("red")
        self.penup()
        self.speed(0)

class Treasure(turtle.Turtle):
    def __init__(self, x, y):
        turtle.Turtle.__init__(self)
        self.shape("circle")
        self.color("gold")
        self.penup()
        self.speed(0)
        self.gold = 100
        self.goto(x, y)

    def destroy(self):
        self.goto(2000, 2000)
        self.hideturtle()

class Player(turtle.Turtle):
    speed = PLAYER_SPEED
    num_moves = NUM_MOVES

    def __init__(self, spawn_position, img):
        turtle.Turtle.__init__(self)

        self.color("blue")
        self.penup()
        # self.speed(0)
        self.shape(img)

        self.move_list = []
        self.fitness = 0
        self.made_goal = 0
        self.col = spawn_position[0]
        self.row = spawn_position[1]


    def move(self, direction):
        # time.sleep(0.1)
        self.showturtle()

        if direction == "right":
            self.col = self.col + 1

            move_to_x = self.xcor() + 100
            move_to_y = self.ycor()
            self.goto(move_to_x,  move_to_y)

        elif direction == "left":
            self.col = self.col - 1

            move_to_x = self.xcor() - 100
            move_to_y = self.ycor()
            self.goto(move_to_x,  move_to_y)
            
        elif direction == "up":
            self.row = self.row - 1

            move_to_x = self.xcor()
            move_to_y = self.ycor() + 100
            self.goto(move_to_x,  move_to_y)

        elif direction == "down":
            self.row = self.row + 1

            move_to_x = self.xcor()
            move_to_y = self.ycor() - 100
            self.goto(move_to_x,  move_to_y)

        else:
            print("unknown move command")

        print((move_to_x,  move_to_y))

    def check_move(self, maze_array):
        """
        Checks to see if the move is ok, and if so, moves the player there. If the player already knows that such a move
        would result in hitting a wall, the function moves the player to a new spot that wouldn't hit a wall and
        returns this move
        """

        if self.speed == 0:
            return

        for i, move in enumerate(self.move_list):
            # Right, Left, Up, Down
            if move == "right":
                new_coord = [self.row, self.col + 1]
            elif move == "left":
                new_coord = [self.row, self.col - 1]
            elif move == "up":
                new_coord = [self.row - 1, self.col]
            elif move == "down":
                new_coord = [self.row + 1, self.col]
            else:
                print(move)
                return

            if maze_array[new_coord[0]][new_coord[1]] == "0":
                self.move(move)
                wn.update()

            elif (maze_array[new_coord[0]][new_coord[1]] == "T"):
                print("Found")
                self.move(move)
                return True
            
            else:
                # Find a new coordinate that is not a wall and not the previous move
                prev_coord = [self.row, self.col]
                new_coord = random.choice([(prev_coord[0], prev_coord[1]+1),
                                           (prev_coord[0], prev_coord[1]-1),
                                           (prev_coord[0]-1, prev_coord[1]),
                                           (prev_coord[0]+1, prev_coord[1])])
                if maze_array[new_coord[0]][new_coord[1]] == "0" and new_coord != prev_coord:
                    self.row, self.col = new_coord
                    # Replace the current position with the new position in the move list
                    self.move_list[i] = self.get_move(prev_coord, new_coord)
            
                    return
                
    def get_move(self, prev_coord, new_coord):
        """
        Gets the appropriate move based on the new and previous coordinates
        """
        if new_coord[0] == prev_coord[0] and new_coord[1] == prev_coord[1] + 1:
            return "right"
        elif new_coord[0] == prev_coord[0] and new_coord[1] == prev_coord[1] - 1:
            return "left"
        elif new_coord[0] == prev_coord[0] + 1 and new_coord[1] == prev_coord[1]:
            return "down"
        elif new_coord[0] == prev_coord[0] - 1 and new_coord[1] == prev_coord[1]:
            return "up"
        else:
            return None
        
    def destroy(self):
        self.goto(2000, 2000)
        self.hideturtle()

def create_random_moves(turns):
    options = MOVE_OPTIONS
    return random.choices(options, k=turns)

def create_moves_array(x = NUM_PLAYERS, y = NUM_MOVES):
    moves = []
    for i in range(x):
        moves.append(create_random_moves(y))

    return moves

def calc_goal_distance(x1, y1, x2, y2, measure="euclidean"):
    if measure=="euclidean":
        goal_dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    elif measure=="manhattan":
        goal_dist = int(abs(abs(x2) - abs(x1)) + abs(abs(y2) - abs(y1)))

    return goal_dist

def uniform_crossover(arr1, arr2, p = 0.5):
    assert len(arr1) == len(arr2), "Arrays must have the same length"
    new_arr = np.empty_like(arr1)
    for i in range(len(arr1)):
        if np.random.rand() < p:
            new_arr[i] = arr1[i]
        else:
            new_arr[i] = arr2[i]
    return new_arr

def mutate(array, mutation_rate=MUTATION_RATE):
    if random.random() <= mutation_rate:
        
        i = random.randint(0, len(array) - 1)
        array[i] = random.choice(MOVE_OPTIONS)
        return array

    else:
        return array

treasures = []

def setup_maze(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            
            character = level[y][x]
            
            screen_x = -860 + (x*100)
            screen_y = 480 - (y*100)

            if character == "X":
                pen.goto(screen_x, screen_y)
                pen.shape("wall1.gif")
                pen.stamp()
            if character == "A":
                pen.goto(screen_x, screen_y)
                pen.shape("wall2.gif")
                pen.stamp()
            if character == "B":
                pen.goto(screen_x, screen_y)
                pen.shape("wall3.gif")
                pen.stamp()
            if character == "C":
                pen.goto(screen_x, screen_y)
                pen.shape("wall4.gif")
                pen.stamp()

            if character == "P":
                player.goto(screen_x, screen_y)
                # player2.goto(screen_x, screen_y)
                player.hideturtle()
                # stack.append([y,x])

            if character == "T":
                treasures.append(Treasure(screen_x, screen_y))

maze = [
    list("XXXBBXXXXXAXXAXXXX"), #0
    list("XPXAAXXXXBBBXXACXX"), #1
    list("X0XCX000000000XXBX"), #2
    list("X0XBX0BBXXXXX0XXBA"), #3
    list("X0XXX0XXCABXA0XXBX"), #4
    list("X0X000XXXBXXB000AX"), #5
    list("X0XX0XX0XACAX0XXXX"), #6
    list("X00T000000000000XX"), #7
    list("X0000000XBAXX0XXXX"), #8
    list("XXXABBAXXXXXBAXXXX"), #9
]

start_point = [1, 1]
goal_point = [7, 3]

pen = Pen()

passW = PassW()
player = Player(start_point, "tia1l.gif")
# player2 = Player("tiar.gif","tial.gif")
setup_maze(maze)

wn.tracer(0)

# time.sleep(0.5)    
# player.destroy()
# passW.clearstamps()
# wn.update()
# passW.shape("pass.gif")

players_moves = create_moves_array()
turn = 1
found = False

screen_x = -860 + (start_point[1] * 100)
screen_y = 480 - (start_point[0] * 100)

## Start
while(found != True and turn < GENERATION_THRESH):
    players = [Player(start_point, "tia1r.gif") for i in range(NUM_PLAYERS)]

    for player in players:
        player.goto(screen_x, screen_y)

    best_fitness = 10000
    best_i = 0

    for i in range(len(players)):
        players[i].move_list = players_moves[i]

        found = players[i].check_move(maze)
        fitness = calc_goal_distance(players[i].row, players[i].col, goal_point[0], goal_point[1])
        players[i].fitness = fitness

        if fitness < best_fitness: 
            best_fitness = fitness
            best_i = i
        
        players[i].destroy()

    best_moves = players[best_i].move_list
    new_players_moves = []

    players.sort(key=lambda x: x.fitness)
    for j in range(len(players)):
        worse_moves = players[j].move_list
        new_moves = uniform_crossover(best_moves, worse_moves)

        new_moves = mutate(new_moves)

        new_players_moves.append(new_moves)

    # for player in players:
    #     player.destroy()
        
    turn += 1
    print(turn)
    print(best_fitness)