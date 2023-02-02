# region import
import pygame
import random
# endregion import

# region CONSTANT
# window settings
WIN_WIDTH, WIN_HEIGHT = 1000, 600
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
TEXT_COLOR = (0, 0, 0)
BUTTON_SELECTED_COLOR = (110, 110, 110)

# game constants
GAME_WIN_WIDTH, GAME_WIN_HEIGHT = 600, 600
MAZE_SIZE = (5, 5)
WALL_WIDTH = 10
GRID_WIDTH, GRID_HEIGHT = (GAME_WIN_WIDTH - ((MAZE_SIZE[1] + 1) * WALL_WIDTH)) / MAZE_SIZE[1], (GAME_WIN_HEIGHT - ((MAZE_SIZE[0] + 1) * WALL_WIDTH)) / MAZE_SIZE[0]
PLAYER_WIDTH, PLAYER_HEIGHT = GRID_WIDTH * 0.45, GRID_HEIGHT * 0.45
PRESS_COOLDOWN = 0.5

# tring constans
FRAME_PER_MOVE = 1
MOVE_PER_EPISODE = MAZE_SIZE[0] * MAZE_SIZE[1]

# text constant
FONT = "Verdana"
FONT_SIZE = 30

# endregion CONSTANT

pygame.init()

# region maze game
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
        pygame.draw.rect(WIN, WALL_COLOR, pygame.Rect(x_coord, GAME_WIN_HEIGHT - WALL_WIDTH, GRID_HEIGHT + 2 * WALL_WIDTH, WALL_WIDTH))
    # vertical
    for row in range(MAZE_SIZE[0]):
        y_coord = row * (GRID_HEIGHT + WALL_WIDTH)
        # left
        pygame.draw.rect(WIN, WALL_COLOR, pygame.Rect(0, y_coord, WALL_WIDTH, GRID_HEIGHT + 2 * WALL_WIDTH))
        # right
        pygame.draw.rect(WIN, WALL_COLOR, pygame.Rect(GAME_WIN_WIDTH - WALL_WIDTH, y_coord, WALL_WIDTH, GRID_HEIGHT + 2 * WALL_WIDTH))

# draw q value

def draw_q_values(q_learning):
    font = pygame.font.SysFont(FONT, int(0.14 * min(GRID_HEIGHT, GRID_WIDTH)))
    for row in range(MAZE_SIZE[0]):
        for col in range(MAZE_SIZE[1]):
            x_coord = col * (GRID_WIDTH + WALL_WIDTH)
            y_coord = row * (GRID_HEIGHT + WALL_WIDTH)
            WIN.blit(font.render(f'{q_learning.q_table[(row, col)][0]:.2f}', True, TEXT_COLOR), (x_coord + WALL_WIDTH + GRID_WIDTH / 3, y_coord + WALL_WIDTH + GRID_HEIGHT / 10))
            WIN.blit(font.render(f'{q_learning.q_table[(row, col)][1]:.2f}', True, TEXT_COLOR), (x_coord + WALL_WIDTH + GRID_WIDTH / 8, y_coord + WALL_WIDTH + GRID_HEIGHT * 4 / 9))
            WIN.blit(font.render(f'{q_learning.q_table[(row, col)][2]:.2f}', True, TEXT_COLOR), (x_coord + WALL_WIDTH + GRID_WIDTH / 3, y_coord + WALL_WIDTH + GRID_HEIGHT * 8 / 10))
            WIN.blit(font.render(f'{q_learning.q_table[(row, col)][3]:.2f}', True, TEXT_COLOR), (x_coord + WALL_WIDTH + GRID_WIDTH * 5 / 9, y_coord + WALL_WIDTH + GRID_HEIGHT *4 / 9))

# draw window
def draw_window(maze, start_point, end_point, player, q_learning, display_q_values, texts):
    # draw background
    WIN.fill(BACKGROUND_COLOR)
    
    # draw maze
    draw_maze(maze, start_point, end_point)

    # draw q values
    if display_q_values:
        draw_q_values(q_learning)

    # draw player 
    pygame.draw.rect(WIN, PLAYER_COLOR, player)

    # draw info
    y_coord = 20
    for text in texts:
        WIN.blit(text, (GAME_WIN_WIDTH + 30, y_coord))    
        y_coord += FONT_SIZE * 13 / 9

    # draw q value button
    font = pygame.font.SysFont(FONT, FONT_SIZE)
    WIN.blit(font.render(f'Q value: ', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30, y_coord))
    WIN.blit(font.render(f'show', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30 + 9 * FONT_SIZE * 0.52, y_coord))
    WIN.blit(font.render(f'hide', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30 + 15 * FONT_SIZE * 0.52, y_coord))
    show_q_values_button = pygame.Rect(GAME_WIN_WIDTH + 30 + 8.5 * FONT_SIZE * 0.52, y_coord + FONT_SIZE * 0.03, 6 * FONT_SIZE * 0.52, FONT_SIZE * 1.3)
    hide_q_values_button = pygame.Rect(GAME_WIN_WIDTH + 30 + 14.5 * FONT_SIZE * 0.52, y_coord + FONT_SIZE * 0.03, 5.1 * FONT_SIZE * 0.52, FONT_SIZE * 1.3)
    if display_q_values:
        pygame.draw.rect(WIN, BUTTON_SELECTED_COLOR, show_q_values_button, int(FONT_SIZE * 0.1), int(FONT_SIZE * 1.2))
    else:
        pygame.draw.rect(WIN, BUTTON_SELECTED_COLOR, hide_q_values_button, int(FONT_SIZE * 0.1), int(FONT_SIZE * 1.2))
    y_coord += FONT_SIZE * 13 / 9

    # upadate window
    pygame.display.update()
    
    return show_q_values_button, hide_q_values_button

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

# endregion maze game

# region Qlearning
class Qlearning():
    # state:player pos:(row, col) action:0->up, 1->left, 2->down, 3->right
    def __init__(self, episodes, epsilon_decay = 0.99, learning_rate = 0.1, discount_factor = 0.5):
        self.epsilon = 1
        self.current_episode = 1
        self.episodes = episodes
        self.epsilon_decay = epsilon_decay
        self.learing_rate = learning_rate
        self.discount_factor = discount_factor
        self.q_table = dict()
        for row in range(MAZE_SIZE[0]):
            for col in range(MAZE_SIZE[1]):
                for a in range(4):
                    self.q_table[(row, col)] = [0, 0, 0, 0]

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 3)
        else:
            actions_q_value = self.q_table[state]
            return actions_q_value.index(max(actions_q_value))
    
    def update_q_value(self, state, state_plus1, action, reward):
        if random.random() < self.epsilon:
            future_reward = self.q_table[state_plus1][random.randint(0, 3)]
        else:
            actions_q_value = self.q_table[state_plus1]
            future_reward = max(actions_q_value)
        self.q_table[state][action] = self.q_table[state][action] + self.learing_rate * (reward + self.discount_factor * future_reward - self.q_table[state][action])
    
    def end_episode(self):
        self.epsilon *= self.epsilon_decay
        self.current_episode += 1

# endregion Qlearning

# region main
# main function
def main():
    clock = pygame.time.Clock()
    run = True

    # init game
    maze = generate_maze(random.randint(1, 65535))
    start_point = pygame.Rect(WALL_WIDTH, WALL_WIDTH, GRID_WIDTH, GRID_HEIGHT)
    end_point = pygame.Rect(GAME_WIN_WIDTH - WALL_WIDTH - GRID_WIDTH, GAME_WIN_HEIGHT - WALL_WIDTH - GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT)
    player = pygame.Rect(WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2, WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2, PLAYER_WIDTH, PLAYER_HEIGHT)
    player_pos = (0, 0)

    # init training
    move_clock = FRAME_PER_MOVE
    move_left = MOVE_PER_EPISODE
    q_learning = Qlearning(100, 0.98)

    # init panel texts
    font = pygame.font.SysFont(FONT, FONT_SIZE)
    texts = []
    texts.append(font.render(f'episode num: {q_learning.current_episode}', True, TEXT_COLOR))
    texts.append(font.render(f'move left: {move_left}', True, TEXT_COLOR))
    
    # init button
    show_q_values = True
    show_q_values_button = pygame.Rect(0, 0, 0, 0)
    hide_q_values_button = pygame.Rect(0, 0, 0, 0)

    # game loop
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # check is show/hide q value button is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                if show_q_values_button.collidepoint(event.pos):
                    show_q_values = True
                if hide_q_values_button.collidepoint(event.pos):
                    show_q_values = False
            # region keyboard control
            # if event.type == pygame.KEYDOWN:
            #     # update player pos from input
            #     player_pos = move_player(maze, player_pos, event.key)
            #     player.x = (WALL_WIDTH + GRID_WIDTH) * player_pos[1] + WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2
            #     player.y = (WALL_WIDTH + GRID_HEIGHT) * player_pos[0] + WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2
                
            #     # check has the player finished
            #     if player.colliderect(end_point):
            #         # restart game
            #         maze, player, player_pos = new_game(maze, player, player_pos)
            # endregion keyboard control

        # make action and update q table
        if move_clock == 0:
            # choose action and move
            player_pos_before = player_pos
            action = q_learning.choose_action(player_pos)
            valid_moves = get_valid_moves(maze, player_pos)
            moved = False
            if action == 0 and (-1, 0) in valid_moves:
                player_pos = (player_pos[0] - 1, player_pos[1])
                moved = True
            elif action == 1 and (0, -1) in valid_moves:
                player_pos = (player_pos[0], player_pos[1] - 1)
                moved = True
            elif action == 2 and (1, 0) in valid_moves:
                player_pos = (player_pos[0] + 1, player_pos[1])
                moved = True
            elif action == 3 and (0, 1) in valid_moves:
                player_pos = (player_pos[0], player_pos[1] + 1)
                moved = True
            player.x = (WALL_WIDTH + GRID_WIDTH) * player_pos[1] + WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2
            player.y = (WALL_WIDTH + GRID_HEIGHT) * player_pos[0] + WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2
            move_left -= 1

            reward = 0
            # calculate reward
            if not moved:
                reward = -1
            if player.colliderect(end_point):
                reward = 10

            # Update Q table
            q_learning.update_q_value(player_pos_before, player_pos, action, reward)

            # update text
            texts[0] = font.render(f'episode num: {q_learning.current_episode}', True, TEXT_COLOR)
            texts[1] = font.render(f'move left: {move_left}', True, TEXT_COLOR)

            # end episode if finish or out of moves
            if move_left == 0 or player.colliderect(end_point):
                q_learning.end_episode()
                player, player_pos = reset_game(player, player_pos)
                move_left = MOVE_PER_EPISODE

            # reset move clock
            move_clock = FRAME_PER_MOVE

        show_q_values_button, hide_q_values_button = draw_window(maze, start_point, end_point, player, q_learning, show_q_values, texts)
        move_clock -= 1

    pygame.quit()

# endregion main

if __name__ == '__main__':
    main()