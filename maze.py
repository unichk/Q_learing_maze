# region import
import pygame
import random
# endregion import

pygame.init()
pygame.mixer.init()

# region CONSTANT
# window settings
WIN_WIDTH, WIN_HEIGHT = 1000, 600
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Maze")

# FPS constant
FPS = 60

# color constants
BACKGROUND_COLOR = (150, 150, 150)
COIN_COLOR = (255, 215, 0)
WALL_COLOR = (0, 0, 0)
BORDER_COLOR = (155, 155, 155)
PLAYER_COLOR = (250, 112, 202)
START_POINT_COLOR = (15, 140, 36)
END_POINT_COLOR = (186, 7, 7)
TEXT_COLOR = (0, 0, 0)
BUTTON_SELECTED_COLOR = (110, 110, 110)

# game constants
GAME_WIN_WIDTH, GAME_WIN_HEIGHT = 600, 600
MAZE_SIZE = (20, 20)
WALL_WIDTH = 10
GRID_WIDTH, GRID_HEIGHT = (GAME_WIN_WIDTH - ((MAZE_SIZE[1] + 1) * WALL_WIDTH)) / MAZE_SIZE[1], (GAME_WIN_HEIGHT - ((MAZE_SIZE[0] + 1) * WALL_WIDTH)) / MAZE_SIZE[0]
PLAYER_WIDTH, PLAYER_HEIGHT = GRID_WIDTH * 0.45, GRID_HEIGHT * 0.45
PRESS_COOLDOWN = 0.5

# tring constans
MOVE_PER_EPISODE = MAZE_SIZE[0] * MAZE_SIZE[1]

# text constant
FONT = "Verdana"
FONT_SIZE = 30

# image
coin_image = pygame.transform.scale(pygame.image.load('coin.png'), (GRID_WIDTH * 0.4, GRID_HEIGHT * 0.4))
wall_image = pygame.image.load('wall.png')
start_point_image = pygame.transform.scale(pygame.image.load('start_point.png'), (GRID_WIDTH * 0.7, GRID_HEIGHT * 0.7))
end_point_image = pygame.transform.scale(pygame.image.load('end_point.png'), (GRID_WIDTH * 0.7, GRID_HEIGHT * 0.7))
player_up = pygame.transform.scale(pygame.image.load('player_up.png'), (PLAYER_WIDTH, PLAYER_HEIGHT))
player_down = pygame.transform.scale(pygame.image.load('player_down.png'), (PLAYER_WIDTH, PLAYER_HEIGHT))
player_left = pygame.transform.scale(pygame.image.load('player_left.png'), (PLAYER_WIDTH, PLAYER_HEIGHT))
player_right = pygame.transform.scale(pygame.image.load('player_right.png'), (PLAYER_WIDTH, PLAYER_HEIGHT))

# sfx
button_click_sfx = pygame.mixer.Sound("button_click_sfx.mp3")
finish_sfx = pygame.mixer.Sound("finish_sfx.mp3")

# endregion CONSTANT

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
    path = []

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
            if next == (MAZE_SIZE[0] - 1, MAZE_SIZE[1] - 1):
                path = stack.copy()
    return maze_vertical_walls, maze_horizontal_walls, path

# draw maze
def draw_maze(maze, start_point, end_point):
    vertical_walls, horizontal_walls = maze

    # draw start and end point
    WIN.blit(start_point_image, (start_point.x + GRID_WIDTH * 0.15, start_point.y + GRID_HEIGHT * 0.15))
    WIN.blit(end_point_image, (end_point.x + GRID_WIDTH * 0.15, end_point.y + GRID_HEIGHT * 0.15))

    vertical_wall_image = pygame.transform.scale(wall_image, (WALL_WIDTH, GRID_HEIGHT + 2 * WALL_WIDTH))
    horizontal_wall_image = pygame.transform.rotate(vertical_wall_image, 90)
    # draw maze wall
    for row in range(MAZE_SIZE[0]):
        for col in range(MAZE_SIZE[1]):
            x_coord = col * (GRID_WIDTH + WALL_WIDTH)
            y_coord = row * (GRID_HEIGHT + WALL_WIDTH)
            # vertical
            if vertical_walls[row][col]:
                WIN.blit(vertical_wall_image, (x_coord, y_coord))
            else:
                pygame.draw.rect(WIN, BORDER_COLOR, pygame.Rect(x_coord, y_coord + WALL_WIDTH, WALL_WIDTH, GRID_HEIGHT))
            # horizontal
            if horizontal_walls[row][col]:
                WIN.blit(horizontal_wall_image, (x_coord, y_coord))
            else:
                pygame.draw.rect(WIN, BORDER_COLOR, pygame.Rect(x_coord + WALL_WIDTH, y_coord, GRID_HEIGHT, WALL_WIDTH))

    # draw maze frame
    # horizontal
    for col in range(MAZE_SIZE[1]):
        x_coord = col * (GRID_WIDTH + WALL_WIDTH)
        # up
        WIN.blit(horizontal_wall_image, (x_coord, 0))
        # down
        WIN.blit(horizontal_wall_image, (x_coord, GAME_WIN_HEIGHT - WALL_WIDTH))
    # vertical
    for row in range(MAZE_SIZE[0]):
        y_coord = row * (GRID_HEIGHT + WALL_WIDTH)
        # left
        WIN.blit(vertical_wall_image, (0, y_coord))
        # right
        WIN.blit(vertical_wall_image, (GAME_WIN_WIDTH - WALL_WIDTH, y_coord))

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
def draw_window(maze, coins, start_point, end_point, player, player_direction, q_learning, display_q_values, texts, speed):
    font = pygame.font.SysFont(FONT, FONT_SIZE)
    # draw background
    WIN.fill(BACKGROUND_COLOR)
    
    # draw maze
    draw_maze(maze, start_point, end_point)

    # draw coin
    for coin in coins:
        WIN.blit(coin_image, coin)

    # draw q values
    if display_q_values:
        draw_q_values(q_learning)

    # draw player 
    if player_direction == "u":
        WIN.blit(player_up, player)
    elif player_direction == "d":
        WIN.blit(player_down, player)
    elif player_direction == "r":
        WIN.blit(player_right, player)
    elif player_direction == "l":
        WIN.blit(player_left, player)
    # draw info
    y_coord = 20
    for text in texts:
        WIN.blit(text, (GAME_WIN_WIDTH + 30, y_coord))    
        y_coord += FONT_SIZE * 13 / 9

    # draw q value button
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

    # draw speed buttons
    WIN.blit(font.render(f'speed: ', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30, y_coord))
    WIN.blit(font.render(f'1', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30 + 8 * FONT_SIZE * 0.52, y_coord))
    WIN.blit(font.render(f'2', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30 + 10 * FONT_SIZE * 0.52, y_coord))
    WIN.blit(font.render(f'3', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30 + 12 * FONT_SIZE * 0.52, y_coord))
    WIN.blit(font.render(f'4', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30 + 14 * FONT_SIZE * 0.52, y_coord))
    WIN.blit(font.render(f'5', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30 + 16 * FONT_SIZE * 0.52, y_coord))
    speed_button = []
    speed_button.append(pygame.Rect(GAME_WIN_WIDTH + 30 + 7.6 * FONT_SIZE * 0.52, y_coord + FONT_SIZE * 0.03, 2 * FONT_SIZE * 0.52, FONT_SIZE * 1.3))
    speed_button.append(pygame.Rect(GAME_WIN_WIDTH + 30 + 9.6 * FONT_SIZE * 0.52, y_coord + FONT_SIZE * 0.03, 2 * FONT_SIZE * 0.52, FONT_SIZE * 1.3))
    speed_button.append(pygame.Rect(GAME_WIN_WIDTH + 30 + 11.6 * FONT_SIZE * 0.52, y_coord + FONT_SIZE * 0.03, 2 * FONT_SIZE * 0.52, FONT_SIZE * 1.3))
    speed_button.append(pygame.Rect(GAME_WIN_WIDTH + 30 + 13.6 * FONT_SIZE * 0.52, y_coord + FONT_SIZE * 0.03, 2 * FONT_SIZE * 0.52, FONT_SIZE * 1.3))
    speed_button.append(pygame.Rect(GAME_WIN_WIDTH + 30 + 15.6 * FONT_SIZE * 0.52, y_coord + FONT_SIZE * 0.03, 2 * FONT_SIZE * 0.52, FONT_SIZE * 1.3))
    pygame.draw.rect(WIN, BUTTON_SELECTED_COLOR, speed_button[speed], int(FONT_SIZE * 0.1), int(FONT_SIZE * 1.2))

    # upadate window
    pygame.display.update()
    
    return show_q_values_button, hide_q_values_button, speed_button

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
    def __init__(self, episodes, epsilon_decay = 0.99, learning_rate = 0.1, discount_factor = 0.8):
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
    *maze, path = generate_maze(random.randint(1, 65535))
    all_coins = []
    for i, grid in enumerate(path):
        if i % 4 == 3:
            all_coins.append(pygame.Rect((WALL_WIDTH + GRID_WIDTH) * grid[1] + WALL_WIDTH + GRID_WIDTH * 0.3, (WALL_WIDTH + GRID_HEIGHT) * grid[0] + WALL_WIDTH + GRID_HEIGHT * 0.3, GRID_WIDTH * 0.4, GRID_HEIGHT * 0.4))
    coins = all_coins.copy()
    start_point = pygame.Rect(WALL_WIDTH, WALL_WIDTH, GRID_WIDTH, GRID_HEIGHT)
    end_point = pygame.Rect(GAME_WIN_WIDTH - WALL_WIDTH - GRID_WIDTH, GAME_WIN_HEIGHT - WALL_WIDTH - GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT)
    player = pygame.Rect(WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2, WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2, PLAYER_WIDTH, PLAYER_HEIGHT)
    player_pos = (0, 0)
    player_direction = "d"
    last_pos = None
    last_last_pos = None

    # init training
    frame_per_move = 10
    move_clock = frame_per_move
    move_left = MOVE_PER_EPISODE
    q_learning = Qlearning(100)
    first_finish_episode = None
    minium_move_spent = 1e9

    # init panel texts
    font = pygame.font.SysFont(FONT, FONT_SIZE)
    texts = []
    texts.append(font.render(f'episode num: {q_learning.current_episode}', True, TEXT_COLOR))
    texts.append(font.render(f'move left: {move_left}', True, TEXT_COLOR))
    texts.append(font.render(f'epsilon: {q_learning.epsilon}', True, TEXT_COLOR))
    texts.append(font.render(f'first success: {first_finish_episode if first_finish_episode != None else " "}', True, TEXT_COLOR))
    texts.append(font.render(f'fastest: {minium_move_spent if minium_move_spent != 1e9 else " "} moves', True, TEXT_COLOR))
    
    # init button
    show_q_values = True
    show_q_values_button = pygame.Rect(0, 0, 0, 0)
    hide_q_values_button = pygame.Rect(0, 0, 0, 0)
    speed = 2 # 0->1,60 1->2,30 2->3,10 3->4,5 4->5,1
    speed_dict = {0:60, 1:30, 2:10, 3:5, 4:1}
    speed_buttons = [pygame.Rect(0, 0, 0, 0)]*5

    # game loop
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # check is show/hide q value button is clicked
                if show_q_values_button.collidepoint(event.pos):
                    show_q_values = True
                    button_click_sfx.play()
                if hide_q_values_button.collidepoint(event.pos):
                    show_q_values = False
                    button_click_sfx.play()
                # check is speed buttons is clicked
                for idx, button in enumerate(speed_buttons):
                    if button.collidepoint(event.pos):
                        speed = idx
                        frame_per_move = speed_dict[idx]
                        button_click_sfx.play()
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
            # fix player direction
            player_pos_before = player_pos
            action = q_learning.choose_action(player_pos)
            valid_moves = get_valid_moves(maze, player_pos)
            moved = False
            if action == 0:
                if (-1, 0) in valid_moves:
                    player_pos = (player_pos[0] - 1, player_pos[1])
                    moved = True
                player_direction = "u"
            elif action == 1:
                if (0, -1) in valid_moves:
                    player_pos = (player_pos[0], player_pos[1] - 1)
                    moved = True
                player_direction = "l"
            elif action == 2:
                if (1, 0) in valid_moves:
                    player_pos = (player_pos[0] + 1, player_pos[1])
                    moved = True
                player_direction = "d"
            elif action == 3:
                if (0, 1) in valid_moves:
                    player_pos = (player_pos[0], player_pos[1] + 1)
                    moved = True
                player_direction = "r"
            player.x = (WALL_WIDTH + GRID_WIDTH) * player_pos[1] + WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2
            player.y = (WALL_WIDTH + GRID_HEIGHT) * player_pos[0] + WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2
            move_left -= 1

            reward = 0
            # calculate reward
            if not moved:
                reward -= 1
            if player.colliderect(end_point):
                reward += 100
                finish_sfx.play()
                if first_finish_episode == None:
                    first_finish_episode = q_learning.current_episode
                minium_move_spent = min(minium_move_spent, MOVE_PER_EPISODE - move_left)
            for coin in coins:
                if player.colliderect(coin):
                    reward += 5
                    coins.remove(coin)
            if player_pos == last_last_pos:
                reward -= 1

            # update player pos history
            last_last_pos = last_pos
            last_pos = player_pos

            # update Q table
            q_learning.update_q_value(player_pos_before, player_pos, action, reward)

            # update text
            texts[0] = font.render(f'episode num: {q_learning.current_episode}', True, TEXT_COLOR)
            texts[1] = font.render(f'move left: {move_left}', True, TEXT_COLOR)
            texts[2] = font.render(f'epsilon: {q_learning.epsilon:.6f}', True, TEXT_COLOR)
            texts[3] = font.render(f'first success: {first_finish_episode if first_finish_episode != None else " "}', True, TEXT_COLOR)
            texts[4] = font.render(f'fastest: {minium_move_spent if minium_move_spent != 1e9 else " "} moves', True, TEXT_COLOR)

            # end episode if finish or out of moves
            if move_left == 0 or player.colliderect(end_point):
                q_learning.end_episode()
                player, player_pos = reset_game(player, player_pos)
                coins = all_coins.copy()
                move_left = MOVE_PER_EPISODE

            # reset move clock
            move_clock = frame_per_move

        show_q_values_button, hide_q_values_button, speed_buttons = draw_window(maze, coins, start_point, end_point, player, player_direction, q_learning, show_q_values, texts, speed)
        move_clock -= 1

    pygame.quit()

# endregion main

if __name__ == '__main__':
    main()