import pygame
import random

# Constants
WINDOW_SIZE = (400, 500)
BACKGROUND_COLOR = (0, 0, 0)  # Black background
GRID_COLOR = (128, 128, 128)
FPS = 25
ZOOM = 20
LEVEL = 2
FONT_SIZE_SMALL = 25
FONT_SIZE_LARGE = 40
WELCOME_FONT_SIZE = 30
SCORE_FONT_COLOR = (255, 255, 255)  # White for visibility on black background
WELCOME_COLOR = (0, 255, 255)  # Cyan for welcome message
PROMPT_COLOR = (255, 255, 0)  # Yellow for input prompt
GAME_OVER_TEXT_COLOR = (255, 125, 0)
GAME_OVER_HINT_COLOR = (255, 215, 0)

# Define colors for figures
COLORS = [
    (0, 0, 0),  # background color (not used in figures)
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]

class Figure:
    FIGURES = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],  # I
        [[4, 5, 9, 10], [2, 6, 5, 9]],  # O
        [[6, 7, 9, 10], [1, 5, 6, 10]],  # T
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],  # S
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],  # Z
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],  # J
        [[1, 2, 5, 6]],  # L
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.FIGURES) - 1)
        self.color = random.randint(1, len(COLORS) - 1)
        self.rotation = 0

    def image(self):
        return self.FIGURES[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.FIGURES[self.type])

class Tetris:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = [[0] * width for _ in range(height)]
        self.score = 0
        self.state = "welcome"
        self.figure = None
        self.x = 100
        self.y = 60
        self.level = LEVEL
        self.username = ""  # Added to store the user's name

    def new_figure(self):
        self.figure = Figure(3, 0)

    def intersects(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if (i + self.figure.y > self.height - 1 or
                        j + self.figure.x > self.width - 1 or
                        j + self.figure.x < 0 or
                        self.field[i + self.figure.y][j + self.figure.x] > 0):
                        return True
        return False

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            if all(self.field[i][j] > 0 for j in range(self.width)):
                lines += 1
                for i1 in range(i, 0, -1):
                    self.field[i1] = self.field[i1 - 1][:]
        self.score += lines ** 2

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

def draw_grid(screen, game):
    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRID_COLOR, [game.x + ZOOM * j, game.y + ZOOM * i, ZOOM, ZOOM], 1)
            if game.field[i][j] > 0:
                pygame.draw.rect(screen, COLORS[game.field[i][j]],
                                 [game.x + ZOOM * j + 1, game.y + ZOOM * i + 1, ZOOM - 2, ZOOM - 1])

def draw_figure(screen, game):
    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(screen, COLORS[game.figure.color],
                                     [game.x + ZOOM * (j + game.figure.x) + 1,
                                      game.y + ZOOM * (i + game.figure.y) + 1,
                                      ZOOM - 2, ZOOM - 2])

def draw_text(screen, game, background_image):
    font_small = pygame.font.SysFont('Calibri', FONT_SIZE_SMALL, True, False)
    font_large = pygame.font.SysFont('Calibri', FONT_SIZE_LARGE, True, False)
    font_welcome = pygame.font.SysFont('Calibri', WELCOME_FONT_SIZE, True, False)

    score_text = font_small.render(f"Score: {game.score}", True, SCORE_FONT_COLOR)
    game_over_text = font_large.render(f"Game Over, {game.username}!", True, GAME_OVER_TEXT_COLOR)
    game_over_score = font_small.render(f"Your Score: {game.score}", True, SCORE_FONT_COLOR)
    game_over_hint = font_small.render("Press R to Restart", True, GAME_OVER_HINT_COLOR)
    welcome_text = font_welcome.render("Welcome to Tetris!", True, WELCOME_COLOR)
    prompt_text = font_small.render("Enter your name:", True, PROMPT_COLOR)

    if game.state == "welcome":
        screen.blit(background_image, (0, 0))  # Draw background image
        # Draw welcome message
        screen.blit(welcome_text, (WINDOW_SIZE[0] // 2 - welcome_text.get_width() // 2, WINDOW_SIZE[1] // 3))
        # Draw prompt for username input
        screen.blit(prompt_text, (WINDOW_SIZE[0] // 2 - prompt_text.get_width() // 2, WINDOW_SIZE[1] // 2 - prompt_text.get_height() // 2))
        pygame.display.flip()
    elif game.state == "gameover":
        screen.fill(BACKGROUND_COLOR)  # Use black background
        screen.blit(game_over_text, (WINDOW_SIZE[0] // 2 - game_over_text.get_width() // 2, WINDOW_SIZE[1] // 3))
        screen.blit(game_over_score, (WINDOW_SIZE[0] // 2 - game_over_score.get_width() // 2, WINDOW_SIZE[1] // 2))
        screen.blit(game_over_hint, (WINDOW_SIZE[0] // 2 - game_over_hint.get_width() // 2, WINDOW_SIZE[1] * 2 // 3))

        # Draw restart button
        button_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - 60, WINDOW_SIZE[1] * 2 // 3 + 50, 120, 50)
        pygame.draw.rect(screen, (255, 0, 0), button_rect)  # Red button
        restart_text = font_small.render("Restart", True, (255, 255, 255))  # White text
        screen.blit(restart_text, (button_rect.x + (button_rect.width - restart_text.get_width()) // 2, button_rect.y + (button_rect.height - restart_text.get_height()) // 2))
    else:
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, game)
        draw_figure(screen, game)
        screen.blit(score_text, [10, 10])

    pygame.display.flip()

def handle_touch_event(event, game):
    x, y = event.pos
    if x < WINDOW_SIZE[0] / 3:
        game.go_side(-1)  # Move left
    elif x > WINDOW_SIZE[0] * 2 / 3:
        game.go_side(1)   # Move right
    elif y > WINDOW_SIZE[1] * 2 / 3:
        game.go_down()    # Move down
    elif y < WINDOW_SIZE[1] / 3:
        game.rotate()     # Rotate

def get_username(background_image):
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Tetris")
    font = pygame.font.SysFont('Calibri', FONT_SIZE_SMALL, True, False)
    input_box = pygame.Rect(WINDOW_SIZE[0] // 2 - 70, WINDOW_SIZE[1] // 2 + 40, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    text = ''
    active = False
    clock = pygame.time.Clock()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return ''
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
        screen.blit(background_image, (0, 0))  # Draw background image
        txt_surface = font.render(text, True, color)
        width = max(140, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(font.render("Enter your name:", True, PROMPT_COLOR), (WINDOW_SIZE[0] // 2 - 90, WINDOW_SIZE[1] // 2 - 50))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()
        clock.tick(30)
    return text

def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris(20, 10)

    # Load background image
    background_image = pygame.image.load('images/tetris7.png')
    background_image = pygame.transform.scale(background_image, WINDOW_SIZE)

    # Welcome screen
    game.state = "welcome"
    username = get_username(background_image)
    game.username = username
    game.state = "start"

    done = False
    pressing_down = False
    counter = 0

    while not done:
        if game.figure is None:
            game.new_figure()
        counter += 1
        if counter > 100000:
            counter = 0

        if counter % (FPS // game.level // 2) == 0 or pressing_down:
            if game.state == "start":
                game.go_down()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate()
                if event.key == pygame.K_DOWN:
                    pressing_down = True
                if event.key == pygame.K_LEFT:
                    game.go_side(-1)
                if event.key == pygame.K_RIGHT:
                    game.go_side(1)
                if event.key == pygame.K_SPACE:
                    game.go_space()
                if event.key == pygame.K_r and game.state == "gameover":
                    game = Tetris(20, 10)
                    game.username = username
                    game.state = "start"
            if event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
                handle_touch_event(event, game)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.state == "gameover":
                    mouse_pos = pygame.mouse.get_pos()
                    button_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - 60, WINDOW_SIZE[1] * 2 // 3 + 50, 120, 50)
                    if button_rect.collidepoint(mouse_pos):
                        game = Tetris(20, 10)
                        game.username = username
                        game.state = "start"

        draw_text(screen, game, background_image)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
