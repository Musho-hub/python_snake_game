import pygame
import sys
import random # Food generation
import os
import math # Visual effects
from collections import deque # Direction queue

class Config:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    SNAKE_SIZE = 20
    FOOD_SIZE = 20
    FPS = 20 
    HIGH_SCORE_FILE = "highscore.txt"

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (51, 156, 55, 0.9)
    RED = (227, 54, 54, 0.9)

    # Fonts
    FONT_SIZE = 36
    FONT_TITLE_SIZE = 72

class Snake:
    def __init__(self):
        self.body = [pygame.Vector2(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2)]
        self.direction = pygame.Vector2(Config.SNAKE_SIZE, 0) # Initial direction: right
        self.next_direction = deque() # Queue for direction changes
        self.growing = False

    def move(self):
        # Update direction from the queue (if available)
        if self.next_direction:
            next_direction = self.next_direction.popleft()
            # Prevent reversing direction
            if next_direction.x != -self.direction.x and next_direction.y != -self.direction.y:
                self.direction = next_direction

        # Move the snake
        new_head = self.body[0] + self.direction
        self.body.insert(0 , new_head)

        if not self.growing:
            self.body.pop()
        else:
            self.growing = False

    def grow(self):
        self.growing = True

    def check_collision(self):
        # Wall collision
        if (self.body[0].x < 0 or self.body[0].x >= Config.SCREEN_WIDTH 
            or
            self.body[0].y < 0 or self.body[0].y >= Config.SCREEN_HEIGHT):
            return True
        # Self collision
        if self.body[0] in self.body[1:]:
            return True
        return False

class Food:
    def __init__(self):
        self.position = self.generate_position()

    def generate_position(self, snake_body):
        while True:
            position = pygame.Vector2(
                random.randint(0, (Config.SCREEN_WIDTH - Config.FOOD_SIZE) // Config.FOOD_SIZE) * Config.FOOD_SIZE,
                random.randint(0 , (Config.SCREEN_HEIGHT - Config.FOOD_SIZE) // Config.FOOD_SIZE) * Config.FOOD_SIZE
            )
            if position not in snake_body:
                return position
            
    def respawn(self, snake_body):
        self.position = self.generate_position(snake_body)
    
    def draw(self):
        pygame.draw.rect(screen, Config.RED, (self.position.x, self.position.y, Config.FOOD_SIZE, Config.FOOD_SIZE))

class GameManager:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        
    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False

    def load_high_score(self):
        if os.path.exists(Config.HIGH_SCORE_FILE):
            with open(Config.HIGH_SCORE_FILE, "r") as file:
                content = file.read().strip()
                if content.isdigit():
                    return int(content)
        return 0
    
    def save_high_score(self):
        with open(Config.HIGH_SCORE_FILE, "w") as file:
            file.write(str(self.high_score))

    def respawn(self):
        self.position = self.generate_position()

    def update(self):
        if not self.game_over:
            self.snake.move()

            if self.snake.body[0] == self.food.position:
                self.food.respawn()
                self.food.respawn(self.snake.body)
                self.score += 1

            if self.snake.check_collision():
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()

    def draw(self, screen):
        screen.fill(Config.BLACK)
        self.snake.move(screen)
        self.food.draw(screen)

        font = pygame.font.Font(None, Config.FONT_SIZE)
        score_text = font.render(f"Score: {self.score}", True, Config.WHITE)
        high_score_text = font.render(f"High Score: {self.high_score}", True, Config.WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))

        if self.game_over:
            game_over_text = font.render("Game over! Press R to Restart or Q to Quit", True, Config.WHITE)
            screen.blit(game_over_text, (Config.SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, Config.SCREEN_HEIGHT // 2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        if len(self.snake.next_direction) < 2:
                            self.snake.next_direction.append(pygame.Vector2(0, -Config.SNAKE_SIZE))
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        if len(self.snake.next_direction) < 2:
                            self.snake.next_direction.append(pygame.Vector2(0, Config.SNAKE_SIZE))
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        if len(self.snake.next_direction) < 2:
                            self.snake.next_direction.append(pygame.Vector2(-Config.SNAKE_SIZE, 0))
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        if len(self.snake.next_direction) < 2:
                            self.snake.next_direction.append(pygame.Vector2(Config.SNAKE_SIZE, 0))
        return True

# Initalize Pygame
pygame.init()

# Screen dimensions
screen_width, screen_height = Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake Game")

# Obejct colors
BG_CLR = Config.BLACK
SNAKE_CLR = Config.GREEN
FOOD_CLR = Config.RED
TXT_CLR = Config.WHITE

# Clock / game variables
clock = pygame.time.Clock()
running = True
game_over = False # Track if the game is over
in_menu = True # Track if the game is in the start menu
dt = 0

# Snake variables
snake_segment_size = Config.SNAKE_SIZE # Size of each snake segment (width and height)
snake = [pygame.Vector2(screen_width // 2, screen_height // 2)] # Snake starts with one segment
snake_direction = pygame.Vector2(snake_segment_size, 0) # Initial direction: right
next_direction_queue = deque() # Queue to store the direction

# Food variables
food_size = Config.FOOD_SIZE
food = pygame.Vector2(
    random.randint(0, (screen_width - food_size) // food_size) * food_size,
    random.randint(0, (screen_height - food_size) // food_size) * food_size
)

# Score variables
score = 0
high_score = 0
font = pygame.font.Font(None, Config.FONT_SIZE) # Default font, size 36
title_font = pygame.font.Font(None, Config.FONT_TITLE_SIZE) # Default font, size 72

# File to store the high score
high_score_file = Config.HIGH_SCORE_FILE

# Function to load the high score from a file
def load_high_score():
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as file:
            content = file.read().strip() # Read and remove any extra whitespace
            if content.isdigit(): # Check if the content is a valid integer
                return int(content)
    return 0 # Default high score if file doesn't exist

# Function to save the high score to a file
def save_high_score(high_score):
    with open(high_score_file, "w") as file:
        file.write(str(high_score))

# Load the high score when the game starts
high_score = load_high_score()

# Function to check for collisions
def check_collisions():
    # Wall collision
    if (
        snake[0].x < 0 or snake[0].x >= screen_width or
        snake[0].y < 0 or snake[0].y >= screen_height
    ):
        print("Wall collision detected!") # Debugging
        return True # Game over
    # Self collision
    for segment in snake[1:]:
        if snake[0] == segment:
            print("Self collision detected")
            return True # Game over
    
    return False # No collision

# Function to reset the game
def reset_game():
    global snake, snake_direction, food, score, game_over, next_direction_queue
    snake = [pygame.Vector2(screen_width // 2, screen_height // 2)] # Reset snake
    snake_direction = pygame.Vector2(snake_segment_size, 0) # Reset direction
    next_direction_queue.clear() # Clear the direction queue
    food = pygame.Vector2(
        random.randint(0, (screen_width - food_size) // food_size) * food_size,
        random.randint(0, (screen_height - food_size) // food_size) * food_size
    ) # Reset food
    score = 0 # Reset score
    game_over = False # Reset game state

# Function to draw the start menu with visual effects
def draw_menu():
    global pulsate_scale, fade_alpha

    # Pulsating effect for the title
    pulsate_scale = 1 + 0.1 * math.sin(pygame.time.get_ticks() * 0.005) # Oscillate between 0. 9 and 1.1
    title_font_scaled = pygame.font.Font(None, int(72 * pulsate_scale))
    # Fading effect for the buttons
    fade_alpha = 255 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.003)) # Oscillate between 128 and 255

    screen.fill(BG_CLR)
    # Draw the title with pulsating effect
    title_text = title_font_scaled.render("Snake Game", True, TXT_CLR)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 100))
    # Draw the start button with fading effect
    start_text = font.render("Press SPACE to Start", True, TXT_CLR)
    start_text.set_alpha(int(fade_alpha)) # Apply fading effect start button
    screen.blit(start_text, (screen_width // 2 - start_text.get_width() // 2, 300))
    # Draw the quit button with fading effect
    quit_text = font.render("Press Q to Quit", True, TXT_CLR)
    quit_text.set_alpha(int(fade_alpha)) # Apply fadding effect quit button
    screen.blit(quit_text, (screen_width // 2 - quit_text.get_width() // 2, 400))
    # Update the display
    pygame.display.flip()

# Game loop
while running:
    if in_menu:
        # Draw the start menu
        draw_menu()
        # Event handling for the menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Start the game
                    in_menu = False
                if event.key == pygame.K_q: # Quit the game
                    running = False
    else:
        # Event handling for the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_over: # Check if the game is over
                    if event.key == pygame.K_r: # Restart the game
                        reset_game()
                    if event.key == pygame.K_q: # Quit the game
                        running = False
                else:
                    # Handle direction changes
                    if event.key == pygame.K_w or event.key == pygame.K_UP:  # UP
                        next_direction_queue.append(pygame.Vector2(0, -snake_segment_size))
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:  # DOWN
                        next_direction_queue.append(pygame.Vector2(0, snake_segment_size))
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:  # LEFT
                        next_direction_queue.append(pygame.Vector2(-snake_segment_size, 0))
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:  # RIGHT
                        next_direction_queue.append(pygame.Vector2(snake_segment_size, 0))

        if not game_over:
            # Update the snake's direction from the queue (only once per frame)
            if next_direction_queue:
                next_direction = next_direction_queue.popleft()
                # Only update the direction if its perpendicular to the current direction
                if next_direction.x != -snake_direction.x and next_direction.y != -snake_direction.y:
                    snake_direction = next_direction

            # Move the snake
            new_head = snake[0] + snake_direction
            snake.insert(0, new_head)

            # Check for food collision
            if snake[0] == food:
                # Move food to a new random position
                food = pygame.Vector2(
                    random.randint(0, (screen_width - food_size) // food_size) * food_size,
                    random.randint(0, (screen_height - food_size) // food_size) * food_size
                )
                # Increase score
                score += 1
            else:
                snake.pop() # Remove the tail if no food was eaten

            # Check for collision
            if check_collisions():
                game_over = True # End the game
                print("Game over!") # Debugging

                # Update the high score if the current score is higher
                if score > high_score:
                    high_score = score
                    save_high_score(high_score) # Save the new high score to the file

        # Draw everything
        screen.fill(BG_CLR)
        for segment in snake:
            # Draw a rectangle for each segment
            pygame.draw.rect(
                    screen, 
                    SNAKE_CLR, 
                    (segment.x, segment.y, snake_segment_size, snake_segment_size)
                )
        # Draw the food
        pygame.draw.rect(
            screen, 
            FOOD_CLR, 
            (food.x, food.y, food_size, food_size)
        )

        # Draw the score and high score
        score_text = font.render(f"Score: {score}", True, TXT_CLR)
        high_score_text = font.render(f"High score {high_score}", True, TXT_CLR)
        screen.blit(score_text, (10, 10)) # Position score in the top-left corner
        screen.blit(high_score_text, (10, 50)) # Position high score below the score

        # Draw game-over screen
        if game_over:
            game_over_text = font.render("Game over! Press R to Restart or Q to Quit", True, TXT_CLR)
            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2))

        # Update the display
        pygame.display.flip()

        # dt is delta time in seconds since last frame, used for framerate
        # Cap the framerate
        dt = clock.tick(Config.FPS) / 1000 # lower fps = slower snake movement

# quit pygame
pygame.quit()
sys.exit()