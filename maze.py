# region import
import pygame
import random
# endregion import

# region pygame init
pygame.init()
pygame.mixer.init()
# endregion pygame init

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
MAZE_SIZE = (5, 5)
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

# region maze game
# maze class
class Maze():
    def __init__(self):
        self.generate_maze(random.randint(1, 65535))
        self.all_coins = []
        for i, grid in enumerate(self.path):
            if i % 4 == 3:
                self.all_coins.append(pygame.Rect((WALL_WIDTH + GRID_WIDTH) * grid[1] + WALL_WIDTH + GRID_WIDTH * 0.3, (WALL_WIDTH + GRID_HEIGHT) * grid[0] + WALL_WIDTH + GRID_HEIGHT * 0.3, GRID_WIDTH * 0.4, GRID_HEIGHT * 0.4))
        self.start_point = pygame.Rect(WALL_WIDTH, WALL_WIDTH, GRID_WIDTH, GRID_HEIGHT)
        self.end_point = pygame.Rect(GAME_WIN_WIDTH - WALL_WIDTH - GRID_WIDTH, GAME_WIN_HEIGHT - WALL_WIDTH - GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT)

    # generate maze with a seed
    def generate_maze(self, seed: int):
        # set seed
        print(f'seed = {seed}')
        random.seed(seed)
        
        # init variables
        self.vertical_walls, self.horizontal_walls = [[True for j in range(MAZE_SIZE[1])] for i in range(MAZE_SIZE[0])], [[True for j in range(MAZE_SIZE[1])] for i in range(MAZE_SIZE[0])]
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
                    self.vertical_walls[grid[0]][grid[1]] = False
                    next = (grid[0], grid[1] - 1)
                elif next == (0, 1):
                    self.vertical_walls[grid[0]][grid[1]+1] = False
                    next = (grid[0], grid[1] + 1)
                elif next == (-1, 0):
                    self.horizontal_walls[grid[0]][grid[1]] = False
                    next = (grid[0] - 1, grid[1])
                elif next == (1, 0):
                    self.horizontal_walls[grid[0] + 1][grid[1]] = False
                    next = (grid[0] + 1, grid[1])
                visited.append(next)
                stack.append(next)
                if next == (MAZE_SIZE[0] - 1, MAZE_SIZE[1] - 1):
                    self.path = stack.copy()
    
    # draw maze
    def draw(self):
        # draw start and end point
        WIN.blit(start_point_image, (self.start_point.x + GRID_WIDTH * 0.15, self.start_point.y + GRID_HEIGHT * 0.15))
        WIN.blit(end_point_image, (self.end_point.x + GRID_WIDTH * 0.15, self.end_point.y + GRID_HEIGHT * 0.15))

        vertical_wall_image = pygame.transform.scale(wall_image, (WALL_WIDTH, GRID_HEIGHT + 2 * WALL_WIDTH))
        horizontal_wall_image = pygame.transform.rotate(vertical_wall_image, 90)
        # draw maze wall
        for row in range(MAZE_SIZE[0]):
            for col in range(MAZE_SIZE[1]):
                x_coord = col * (GRID_WIDTH + WALL_WIDTH)
                y_coord = row * (GRID_HEIGHT + WALL_WIDTH)
                # vertical
                if self.vertical_walls[row][col]:
                    WIN.blit(vertical_wall_image, (x_coord, y_coord))
                else:
                    pygame.draw.rect(WIN, BORDER_COLOR, pygame.Rect(x_coord, y_coord + WALL_WIDTH, WALL_WIDTH, GRID_HEIGHT))
                # horizontal
                if self.horizontal_walls[row][col]:
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

# get all valid move of a grid
def get_neighbor_girds(grid: tuple[int, int]) -> list[tuple[int, int]]:
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

# draw q value
def draw_q_values(q_learning: Qlearning):
    font = pygame.font.SysFont(FONT, int(0.14 * min(GRID_HEIGHT, GRID_WIDTH)))
    for row in range(MAZE_SIZE[0]):
        for col in range(MAZE_SIZE[1]):
            x_coord = col * (GRID_WIDTH + WALL_WIDTH)
            y_coord = row * (GRID_HEIGHT + WALL_WIDTH)
            WIN.blit(font.render(f'{q_learning.q_table[(row, col)][0]:.2f}', True, TEXT_COLOR), (x_coord + WALL_WIDTH + GRID_WIDTH / 3, y_coord + WALL_WIDTH + GRID_HEIGHT / 10))
            WIN.blit(font.render(f'{q_learning.q_table[(row, col)][1]:.2f}', True, TEXT_COLOR), (x_coord + WALL_WIDTH + GRID_WIDTH / 8, y_coord + WALL_WIDTH + GRID_HEIGHT * 4 / 9))
            WIN.blit(font.render(f'{q_learning.q_table[(row, col)][2]:.2f}', True, TEXT_COLOR), (x_coord + WALL_WIDTH + GRID_WIDTH / 3, y_coord + WALL_WIDTH + GRID_HEIGHT * 8 / 10))
            WIN.blit(font.render(f'{q_learning.q_table[(row, col)][3]:.2f}', True, TEXT_COLOR), (x_coord + WALL_WIDTH + GRID_WIDTH * 5 / 9, y_coord + WALL_WIDTH + GRID_HEIGHT *4 / 9))

# player class
class Player():
    def __init__(self):
        self.rect = pygame.Rect(WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2, WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.pos = (0, 0)
        self.direction = "d"
        self.last_pos = None
        self.last_last_pos = None

# player class
class Button():
    def __init__(self, select: bool = False):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.word =  None
        self.word_pos = None
        self.select = select
    
    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        if self.rect.collidepoint(mouse_pos):
            button_click_sfx.play()
            return True
        return False
    
    def draw(self):
        WIN.blit(self.word, self.word_pos)
        if self.select:
            pygame.draw.rect(WIN, BUTTON_SELECTED_COLOR, self.rect, int(FONT_SIZE * 0.1), int(FONT_SIZE * 1.2))

# select buttons class
class Select_buttons():
    def __init__(self, len: int):
        self.buttons = [Button() for _ in range(len)]
    
    def select(self, mouse_pos: tuple[int, int]) -> int:
        for idx, button in enumerate(self.buttons):
            if button.is_clicked(mouse_pos):
                for b in self.buttons:
                    b.select = False
                button.select = True
                return idx

# panel class
class Panel():
    def __init__(self):
        self.texts = []
        self.texts_pos = []
        self.show_hide_q_values_buttons = Select_buttons(2)
        self.show_hide_q_values_buttons.buttons[0].select = True
        self.speed_buttons = Select_buttons(5)
        self.speed_buttons.buttons[2].select = True
    
    def init_panel(self):
        font = pygame.font.SysFont(FONT, FONT_SIZE)
        
        # init texts pos
        y_coord = 20
        for _ in self.texts:
            self.texts_pos.append((GAME_WIN_WIDTH + 30, y_coord))
            y_coord += FONT_SIZE * 13 / 9
        
        # init show/hide q values button
        self.texts.append(font.render(f'Q value: ', True, TEXT_COLOR))
        self.texts_pos.append((GAME_WIN_WIDTH + 30, y_coord))
        self.show_hide_q_values_buttons.buttons[0].word, self.show_hide_q_values_buttons.buttons[0].word_pos = font.render(f'show', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30 + 9 * FONT_SIZE * 0.52, y_coord)
        self.show_hide_q_values_buttons.buttons[1].word, self.show_hide_q_values_buttons.buttons[1].word_pos = font.render(f'hide', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30 + 15 * FONT_SIZE * 0.52, y_coord)
        self.show_hide_q_values_buttons.buttons[0].rect = pygame.Rect(GAME_WIN_WIDTH + 30 + 8.5 * FONT_SIZE * 0.52, y_coord + FONT_SIZE * 0.03, 6 * FONT_SIZE * 0.52, FONT_SIZE * 1.3)
        self.show_hide_q_values_buttons.buttons[1].rect = pygame.Rect(GAME_WIN_WIDTH + 30 + 14.5 * FONT_SIZE * 0.52, y_coord + FONT_SIZE * 0.03, 5.1 * FONT_SIZE * 0.52, FONT_SIZE * 1.3)
        y_coord += FONT_SIZE * 13 / 9

        # init speed buttons
        self.texts.append(font.render(f'speed: ', True, TEXT_COLOR))
        self.texts_pos.append((GAME_WIN_WIDTH + 30, y_coord))
        for i in range(5):
            self.speed_buttons.buttons[i].word, self.speed_buttons.buttons[i].word_pos = font.render(f'{i + 1}', True, TEXT_COLOR), (GAME_WIN_WIDTH + 30 + (8 + 2 * i) * FONT_SIZE * 0.52, y_coord)
            self.speed_buttons.buttons[i].rect = pygame.Rect(GAME_WIN_WIDTH + 30 + (8 + 2 * i - 0.4) * FONT_SIZE * 0.52, y_coord + FONT_SIZE * 0.03, 2 * FONT_SIZE * 0.52, FONT_SIZE * 1.3)

    # draw panel
    def draw(self):
        # draw info
        y_coord = 20
        for idx, text in enumerate(self.texts):
            WIN.blit(text, self.texts_pos[idx])    
            y_coord += FONT_SIZE * 13 / 9

        # draw q value button
        self.show_hide_q_values_buttons.buttons[0].draw()
        self.show_hide_q_values_buttons.buttons[1].draw()
        y_coord += FONT_SIZE * 13 / 9

        # draw speed buttons
        for i in range(5):
            self.speed_buttons.buttons[i].draw()

# draw window
def draw_window(maze: Maze, coins: list[pygame.Rect], player: Player, q_learning: Qlearning, panel: Panel, display_q_values: bool):
    # draw background
    WIN.fill(BACKGROUND_COLOR)
    
    # draw maze
    maze.draw()

    # draw coin
    for coin in coins:
        WIN.blit(coin_image, coin)

    # draw q values
    if display_q_values:
        draw_q_values(q_learning)

    # draw player 
    if player.direction == "u":
        WIN.blit(player_up, player)
    elif player.direction == "d":
        WIN.blit(player_down, player)
    elif player.direction == "r":
        WIN.blit(player_right, player)
    elif player.direction == "l":
        WIN.blit(player_left, player)

    # draw panel
    panel.draw()

    # upadate window
    pygame.display.update()

# get all valid moves of the position
def get_valid_moves(maze: Maze, player: Player) -> list[tuple[int, int]]:
    neighbor_grids = get_neighbor_girds(player.pos)

    valid_moves = []
    if ((0, -1) in neighbor_grids) and (maze.vertical_walls[player.pos[0]][player.pos[1]] == False):
        valid_moves.append((0, -1))
    if ((0, 1) in neighbor_grids) and (maze.vertical_walls[player.pos[0]][player.pos[1] + 1] == False):
        valid_moves.append((0, 1))
    if ((-1, 0) in neighbor_grids) and (maze.horizontal_walls[player.pos[0]][player.pos[1]] == False):
        valid_moves.append((-1, 0))
    if ((1, 0) in neighbor_grids) and (maze.horizontal_walls[player.pos[0] + 1][player.pos[1]] == False):
        valid_moves.append((1, 0))

    return valid_moves

# move player with wasd (to be fix)
def move_player_keyboard(maze: Maze, player: Player, keys_pressed):
    valid_moves = get_valid_moves(maze, player.pos)
    if (keys_pressed == pygame.K_w) and ((-1, 0) in valid_moves):
        player.pos = (player.pos[0] - 1, player.pos[1])
    if (keys_pressed == pygame.K_a) and ((0, -1) in valid_moves):
        player.pos = (player.pos[0], player.pos[1] - 1)
    if (keys_pressed == pygame.K_s) and ((1, 0) in valid_moves):
        player.pos = (player.pos[0] + 1, player.pos[1])
    if (keys_pressed == pygame.K_d) and ((0, 1) in valid_moves):
        player.pos = (player.pos[0], player.pos[1] + 1)

    return player

# move player with input action
def move_player(maze: Maze, player: Player, action: str) -> bool:
    valid_moves = get_valid_moves(maze, player)
    moved = False
    if action == 0:
        if (-1, 0) in valid_moves:
            player.pos = (player.pos[0] - 1, player.pos[1])
            moved = True
        player.direction = "u"
    elif action == 1:
        if (0, -1) in valid_moves:
            player.pos = (player.pos[0], player.pos[1] - 1)
            moved = True
        player.direction = "l"
    elif action == 2:
        if (1, 0) in valid_moves:
            player.pos = (player.pos[0] + 1, player.pos[1])
            moved = True
        player.direction = "d"
    elif action == 3:
        if (0, 1) in valid_moves:
            player.pos = (player.pos[0], player.pos[1] + 1)
            moved = True
        player.direction = "r"
    player.rect.x = (WALL_WIDTH + GRID_WIDTH) * player.pos[1] + WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2
    player.rect.y = (WALL_WIDTH + GRID_HEIGHT) * player.pos[0] + WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2

    return moved

# new game (to be fix)
def new_game(maze: Maze, player: Player):
    maze = Maze()
    player.rect = pygame.Rect(WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2, WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2, PLAYER_WIDTH, PLAYER_HEIGHT)
    player.pos = (0, 0)
    return maze, player

# reset game
def reset_game(player: Player) -> Player:
    player.rect = pygame.Rect(WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2, WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2, PLAYER_WIDTH, PLAYER_HEIGHT)
    player.pos = (0, 0)
    return player

# endregion maze game

# region main
# main function
def main():
    clock = pygame.time.Clock()
    run = True

    # init game
    maze = Maze()
    coins = maze.all_coins.copy()
    player = Player()

    # init training
    frame_per_move = 10
    move_clock = frame_per_move
    move_left = MOVE_PER_EPISODE
    q_learning = Qlearning(100)
    first_finish_episode = None
    minium_move_spent = 1e9

    # init panel
    panel = Panel()
    font = pygame.font.SysFont(FONT, FONT_SIZE)
    panel.texts.append(font.render(f'episode num: {q_learning.current_episode}', True, TEXT_COLOR))
    panel.texts.append(font.render(f'move left: {move_left}', True, TEXT_COLOR))
    panel.texts.append(font.render(f'epsilon: {q_learning.epsilon}', True, TEXT_COLOR))
    panel.texts.append(font.render(f'first success: {first_finish_episode if first_finish_episode != None else " "}', True, TEXT_COLOR))
    panel.texts.append(font.render(f'fastest: {minium_move_spent if minium_move_spent != 1e9 else " "} moves', True, TEXT_COLOR))
    panel.init_panel()
    
    # init control settings
    show_q_values = True
    speed = 2 # 0->1,60 1->2,30 2->3,10 3->4,5 4->5,1
    speed_dict = {0:60, 1:30, 2:10, 3:5, 4:1}

    # game loop
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # check is show/hide q value button is clicked
                button_clicked = panel.show_hide_q_values_buttons.select(event.pos)
                if button_clicked != None:
                    show_q_values = True if show_q_values == 0 else False
                # check is speed buttons is clicked
                button_clicked = panel.speed_buttons.select(event.pos)
                if button_clicked != None:
                    speed = button_clicked
                    frame_per_move = speed_dict[speed]
            # region keyboard control
            # if event.type == pygame.KEYDOWN:
            #     # update player pos from input
            #     player.pos = move_player(maze, player, event.key)
            #     player.rect.x = (WALL_WIDTH + GRID_WIDTH) * player.pos[1] + WALL_WIDTH + GRID_WIDTH / 2  - PLAYER_WIDTH / 2
            #     player.rect.y = (WALL_WIDTH + GRID_HEIGHT) * player.pos[0] + WALL_WIDTH + GRID_HEIGHT / 2  - PLAYER_HEIGHT / 2
                
            #     # check has the player finished
            #     if player.rect.colliderect(end_point):
            #         # restart game
            #         maze, player = new_game(maze, player)
            # endregion keyboard control

        # make action and update q table
        if move_clock == 0:
            # choose action and move
            player_pos_before = player.pos
            action = q_learning.choose_action(player.pos)
            moved = move_player(maze, player, action)
            move_left -= 1

            # calculate reward
            reward = 0
            if not moved:
                reward -= 1
            if player.rect.colliderect(maze.end_point):
                reward += 100
                finish_sfx.play()
                if first_finish_episode == None:
                    first_finish_episode = q_learning.current_episode
                minium_move_spent = min(minium_move_spent, MOVE_PER_EPISODE - move_left)
            for coin in coins:
                if player.rect.colliderect(coin):
                    reward += 5
                    coins.remove(coin)
            if player.pos == player.last_last_pos:
                reward -= 1

            # update player pos history
            player.last_last_pos = player.last_pos
            player.last_pos = player.pos

            # update Q table
            q_learning.update_q_value(player_pos_before, player.pos, action, reward)

            # update panel text
            panel.texts[0] = font.render(f'episode num: {q_learning.current_episode}', True, TEXT_COLOR)
            panel.texts[1] = font.render(f'move left: {move_left}', True, TEXT_COLOR)
            panel.texts[2] = font.render(f'epsilon: {q_learning.epsilon:.6f}', True, TEXT_COLOR)
            panel.texts[3] = font.render(f'first success: {first_finish_episode if first_finish_episode != None else " "}', True, TEXT_COLOR)
            panel.texts[4] = font.render(f'fastest: {minium_move_spent if minium_move_spent != 1e9 else " "} moves', True, TEXT_COLOR)

            # end episode if finish or out of moves
            if move_left == 0 or player.rect.colliderect(maze.end_point):
                q_learning.end_episode()
                player = reset_game(player)
                coins = maze.all_coins.copy()
                move_left = MOVE_PER_EPISODE

            # reset move clock
            move_clock = frame_per_move

            draw_window(maze, coins, player, q_learning, panel, show_q_values)
        
        move_clock -= 1

    pygame.quit()

# endregion main

if __name__ == '__main__':
    main()