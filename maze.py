import pygame
import random

# window settings
WIN_WIDTH, WIN_HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Maze")

# FPS constant
FPS = 60

# color constants
BACKGROUND_COLOR = (150, 150, 150)
WALL_COLOR = (0, 0, 0)
BORDER_COLOR = (155, 155, 155)
PLAYER_COLOR = (250, 112, 202)
START_POINT_COLOR = (15, 140, 36)
END_POINT_COLOR = (186, 7, 7)

# game constants
MAZE_SIZE = (5, 5)
WALL_WIDTH = 10
GRID_WIDTH, GRID_HEIGHT = (WIN_WIDTH - ((MAZE_SIZE[1] + 1) * WALL_WIDTH)) / MAZE_SIZE[1], (WIN_HEIGHT - ((MAZE_SIZE[0] + 1) * WALL_WIDTH)) / MAZE_SIZE[0]
PLAYER_WIDTH, PLAYER_HEIGHT = GRID_WIDTH * 0.45, GRID_HEIGHT * 0.45
PRESS_COOLDOWN = 0.5

# get all valid move of a grid
def get_neighbor_girds(grid):
    row, col = grid
    valid_moves = [(0, 1), (0, -1), (-1, 0), (1, 0)]
    if col == 0:
        valid_moves.remove((0, -1))
    if col == MAZE_SIZE[1] - 1:
        valid_moves.remove((0, 1))
    if row == 0:
        valid_moves.remove((-1, 0))
    if row == MAZE_SIZE[0] - 1:
        valid_moves.remove((1, 0))
    return valid_moves

# generate maze with a seed
def generate_maze(seed):
    # set seed
    print(f'seed = {seed}')
    random.seed(seed)
    
    # init variables
    maze_vertical_walls, maze_horizontal_walls = [[True for j in range(MAZE_SIZE[1])] for i in range(MAZE_SIZE[0])], [[True for j in range(MAZE_SIZE[1])] for i in range(MAZE_SIZE[0])]
    start_grid = (0, 0)
    visited = [start_grid]
    stack = [start_grid]

    # DFS
    while len(stack) > 0:
        # get unvisited neighbors
        grid = stack.pop()
        moves = get_neighbor_girds(grid)
        unvisited_neighbors = []
        for move in moves:
            if (grid[0] + move[0], grid[1] + move[1]) not in visited:
                unvisited_neighbors.append(move)
        
        # remove wall randomly if have unvisited neighbors
        if len(unvisited_neighbors) > 0:
            stack.append(grid)
            next = random.choice(unvisited_neighbors)
            if next == (0, -1):
                maze_vertical_walls[grid[0]][grid[1]] = False
                next = (grid[0], grid[1] - 1)
            elif next == (0, 1):
                maze_vertical_walls[grid[0]][grid[1]+1] = False
                next = (grid[0], grid[1] + 1)
            elif next == (-1, 0):
                maze_horizontal_walls[grid[0]][grid[1]] = False
                next = (grid[0] - 1, grid[1])
            elif next == (1, 0):
                maze_horizontal_walls[grid[0] + 1][grid[1]] = False
                next = (grid[0] + 1, grid[1])
            visited.append(next)
            stack.append(next)
    
    return maze_vertical_walls, maze_horizontal_walls

# draw maze
def draw_maze(maze, start_point, end_point):
    vertical_walls, horizontal_walls = maze

    # draw start and end point
    pygame.draw.rect(WIN, START_POINT_COLOR, start_point)
    pygame.draw.rect(WIN, END_POINT_COLOR, end_point)

    # draw maze wall
    for row in range(MAZE_SIZE[0]):
        for col in range(MAZE_SIZE[1]):
            x_coord = col * (GRID_WIDTH + WALL_WIDTH)
            y_coord = row * (GRID_HEIGHT + WALL_WIDTH)
            # vertical
            if vertical_walls[row][col]:
                pygame.draw.rect(WIN, WALL_COLOR, pygame.Rect(x_coord, y_coord, WALL_WIDTH, GRID_HEIGHT + 2 * WALL_WIDTH))
            else:
                pygame.draw.rect(WIN, BORDER_COLOR, pygame.Rect(x_coord, y_coord + WALL_WIDTH, WALL_WIDTH, GRID_HEIGHT))
            # horizontal
            if horizontal_walls[row][col]:
                pygame.draw.rect(WIN, WALL_COLOR, pygame.Rect(x_coord, y_coord, GRID_HEIGHT + 2 * WALL_WIDTH, WALL_WIDTH))
            else:
                pygame.draw.rect(WIN, BORDER_COLOR, pygame.Rect(x_coord + WALL_WIDTH, y_coord, GRID_HEIGHT, WALL_WIDTH))

    # draw maze frame
    # horizontal
    for col in range(MAZE_SIZE[1]):
        x_coord = col * (GRID_WIDTH + WALL_WIDTH)
        # up
        pygame.draw.rect(WIN, WALL_COLOR, pygame.Rect(x_coord, 0,  GRID_HEIGHT + 2 * WALL_WIDTH, WALL_WIDTH))
        # down
        pygame.draw.rect(WIN, WALL_COLOR, pygame.Rect(x_coord, WIN_HEIGHT - WALL_WIDTH, GRID_HEIGHT + 2 * WALL_WIDTH, WALL_WIDTH))
    # vertical
    for row in range(MAZE_SIZE[0]):
        y_coord = row * (GRID_HEIGHT + WALL_WIDTH)
        # left
        pygame.draw.rect(WIN, WALL_COLOR, pygame.Rect(0, y_coord, WALL_WIDTH, GRID_HEIGHT + 2 * WALL_WIDTH))
        # right
        pygame.draw.rect(WIN, WALL_COLOR, pygame.Rect(WIN_WIDTH - WALL_WIDTH, y_coord, WALL_WIDTH, GRID_HEIGHT + 2 * WALL_WIDTH))

# draw window
def draw_window(maze, start_point, end_point, player):
    # draw background
    WIN.fill(BACKGROUND_COLOR)
    
    # draw maze
    draw_maze(maze, start_point, end_point)

    # draw player 
    pygame.draw.rect(WIN, PLAYER_COLOR, player)

    # upadate window
    pygame.display.update()

# get all valid moves of the position
def get_valid_moves(maze, player_pos):
    vertical_walls, horizontal_walls = maze
    neighbor_grids = get_neighbor_girds(player_pos)

    valid_moves = []
    if ((0, -1) in neighbor_grids) and (vertical_walls[player_pos[0]][player_pos[1]] == False):
        valid_moves.append((0, -1))
    if ((0, 1) in neighbor_grids) and (vertical_walls[player_pos[0]][player_pos[1] + 1] == False):
        valid_moves.append((0, 1))
    if ((-1, 0) in neighbor_grids) and (horizontal_walls[player_pos[0]][player_pos[1]] == False):
        valid_moves.append((-1, 0))
    if ((1, 0) in neighbor_grids) and (horizontal_walls[player_pos[0] + 1][player_pos[1]] == False):
        valid_moves.append((1, 0))

    return valid_moves

# move player with wasd
def move_player(maze, player_pos, keys_pressed):
    valid_moves = get_valid_moves(maze, player_pos)
    if (keys_pressed == pygame.K_w) and ((-1, 0) in valid_moves):
        player_pos = (player_pos[0] - 1, player_pos[1])
    if (keys_pressed == pygame.K_a) and ((0, -1) in valid_moves):
        player_pos = (player_pos[0], player_pos[1] - 1)
    if (keys_pressed == pygame.K_s) and ((1, 0) in valid_moves):
        player_pos = (player_pos[0] + 1, player_pos[1])
    if (keys_pressed == pygame.K_d) and ((0, 1) in valid_moves):
        player_pos = (player_pos[0], player_pos[1] + 1)

    return player_pos

# new game
def new_game(maze, player, player_pos):
    maze = generate_maze(random.randint(1, 65535))
    player = pygame.Rect(WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2, WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2, PLAYER_WIDTH, PLAYER_HEIGHT)
    player_pos = (0, 0)
    return maze, player, player_pos

# reset game
def reset_game(player, player_pos):
    player = pygame.Rect(WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2, WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2, PLAYER_WIDTH, PLAYER_HEIGHT)
    player_pos = (0, 0)
    return player, player_pos

# main function
def main():
    clock = pygame.time.Clock()
    run = True

    # init game
    maze = generate_maze(random.randint(1, 65535))
    start_point = pygame.Rect(WALL_WIDTH, WALL_WIDTH, GRID_WIDTH, GRID_HEIGHT)
    end_point = pygame.Rect(WIN_WIDTH - WALL_WIDTH - GRID_WIDTH, WIN_HEIGHT - WALL_WIDTH - GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT)
    player = pygame.Rect(WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2, WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2, PLAYER_WIDTH, PLAYER_HEIGHT)
    player_pos = (0, 0)

    # game loop
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # update player pos from input
                player_pos = move_player(maze, player_pos, event.key)
                player.x = (WALL_WIDTH + GRID_WIDTH) * player_pos[1] + WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2
                player.y = (WALL_WIDTH + GRID_HEIGHT) * player_pos[0] + WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2
                
                # check has the player finished
                if player.colliderect(end_point):
                    # restart game
                    maze, player, player_pos = new_game(maze, player, player_pos)

        draw_window(maze, start_point, end_point, player)

    pygame.quit()

if __name__ == '__main__':
    main()