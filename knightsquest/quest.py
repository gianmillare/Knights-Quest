# Import the dependencies
import pgzrun
import random

# Create the initial window and grid
GRID_WIDTH = 16
GRID_HEIGHT = 12
GRID_SIZE = 50

# Guard movement
GUARD_MOVE_INTERVAL = 0.5
# Player movement
PLAYER_MOVE_INTERVAL = 0.1
# Randomizing background tiles for realism
BACKGROUND_SEED = 123456

WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE

# Draw the map
MAP = ["WWWWWWWWWWWWWWWW",
       "W              W",
       "W              W",
       "W  W  KG       W",
       "W  WWWWWWWWWW  W",
       "W              W",
       "W      P       W",
       "W  WWWWWWWWWW  W",
       "W        GK W  W",
       "W              W",
       "W              D",
       "WWWWWWWWWWWWWWWW"]
# Draw the floor of the dungeon
def screen_coords(x, y):
    return (x * GRID_SIZE, y * GRID_SIZE)

# adding a utility function to locate the actor-player
def grid_coords(actor):
    return (round(actor.x / GRID_SIZE), round(actor.y / GRID_SIZE))

# Create an actor for the player, create objectives (keys)
def setup_game():
    global game_over, player_won, player, keys_to_collect, guards
    game_over = False
    player_won = False
    player = Actor("player", anchor=("left", "top"))
    keys_to_collect = []
    guards = []
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            square = MAP[y][x]
            if square =="P":
                player.pos = screen_coords(x,y)
            elif square == "K":
                key = Actor("key", anchor=("left", "top"), pos=screen_coords(x, y))
                keys_to_collect.append(key)
            elif square == "G":
                guard = Actor("guard", anchor=("left", "top"), pos=screen_coords(x, y))
                guards.append(guard)

def draw_background():
    random.seed(BACKGROUND_SEED)
    for y in range (GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if x % 2== y % 2:
                screen.blit("floor1", screen_coords(x, y))
            else:
                screen.blit("floor2", screen_coords(x, y))
            
            # Start the draw loop to make cracks in the background
            n = random.randint(0, 99)
            if n < 5:
                screen.blit("crack1", screen_coords(x, y))
            elif n < 10:
                screen.blit("crack2", screen_coords(x, y))

def draw_scenery():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            square = MAP[y][x]
            if square == "W":
                screen.blit("wall", screen_coords(x, y))
            elif square == "D":
                screen.blit("door", screen_coords(x, y))

# Draw the actors and the objectives
def draw_actors():
    player.draw()
    for key in keys_to_collect:
        key.draw()
    for guard in guards:
        guard.draw()

# Create a Game Over sign that appears once the objective is complete
def draw_game_over():
    screen_middle = (WIDTH / 2, HEIGHT / 2)
    screen.draw.text("GAME OVER", midbottom=screen_middle, 
                     fontsize=GRID_SIZE, color="cyan", owidth=1)
    if player_won:
        screen.draw.text("YOU WON!", midtop=screen_middle,
                         fontsize=GRID_SIZE, color="green", owidth=1)
    else:
        screen.draw.text("YOU LOST!", midtop=screen_middle,
                         fontsize=GRID_SIZE, color="red", owidth=1)
    
    # Create a message for the player to restart the game using the spacebar
    screen.draw.text("Press SPACE to play again", midtop=(WIDTH / 2, HEIGHT / 2 + GRID_SIZE),
                     fontsize=GRID_SIZE / 2, color="cyan", owidth=1)
        
def draw():
    draw_background()
    draw_scenery()
    draw_actors()
    if game_over:
        draw_game_over()

# Create a function to enable restarting the game
def on_key_up(key):
    if key == keys.SPACE and game_over:
        setup_game()
        
# Create a function that will control the player using keys
def on_key_down(key):
    if key == keys.LEFT:
        move_player(-1, 0)
    elif key == keys.UP:
        move_player(0, -1)
    elif key == keys.RIGHT:
        move_player(1, 0)
    elif key == keys.DOWN:
        move_player(0, 1)

# Create a function that will move the player once a key is pressed
def move_player(dx, dy):
    global game_over, player_won
    if game_over:
        return
    (x, y) = grid_coords(player)
    x += dx
    y += dy
    square = MAP[y][x]
    if square == "W":
        return
    elif square == "D":
        if len(keys_to_collect) > 0:
            return
        else:
            game_over = True
            player_won = True
    for key in keys_to_collect:
        (key_x, key_y) = grid_coords(key)
        if x == key_x and y == key_y:
            keys_to_collect.remove(key)
            break
    # adding after creating the animation for player movement
    animate(player, pos=screen_coords(x, y), duration=PLAYER_MOVE_INTERVAL)
    #player.pos = screen_coords(x, y)
    
# Create a function that will move the guards, adding difficulty to the game
def move_guard(guard):
    global game_over
    if game_over:
        return
    (player_x, player_y) = grid_coords(player)
    (guard_x, guard_y) = grid_coords(guard)
    if player_x > guard_x and MAP[guard_y][guard_x + 1] != "W":
        guard_x += 1
    elif player_x < guard_x and MAP[guard_y][guard_x - 1] != "W":
        guard_x -= 1
    elif player_y > guard_y and MAP[guard_y + 1][guard_x] != "W":
        guard_y += 1
    elif player_y < guard_y and MAP[guard_y -1][guard_x] != "W":
        guard_y -= 1
    
    # animate the guards to move freely across the map
    animate(guard, pos=screen_coords(guard_x, guard_y), duration=GUARD_MOVE_INTERVAL)
    #guard.pos = screen_coords(guard_x, guard_y)
    if guard_x == player_x and guard_y == player_y:
        game_over = True

def move_guards():
    for guard in guards:
        move_guard(guard)

setup_game()

# Schedule the movement of the guards
clock.schedule_interval(move_guards, GUARD_MOVE_INTERVAL)

pgzrun.go()