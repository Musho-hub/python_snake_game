import pygame
import sys
import random # For generating random positions for the food
import os # For file operations (loading/saving high score)
import math # Visual effects
from collections import deque # For managing direction changes in the snake

class Config:
    # Configuration settings for the game
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    SNAKE_SIZE = 20 # Size of each snake segment
    FOOD_SIZE = 20 # Size of food
    FPS = 20 # Frames per second (controls game speed - higher FPS the faster snake moves)
    HIGH_SCORE_FILE = "highscore.txt" # File to store the high score

    # Colors
    BLACK = (0, 0, 0) # Background color
    WHITE = (255, 255, 255) # Text color
    GREEN = (51, 156, 55) # Snake color
    RED = (227, 54, 54) # Food color

    # Font sizes
    FONT_SIZE = 36 # Regular font size for text
    FONT_TITLE_SIZE = 72 # Larger font size for titles

class Snake:
    def __init__(self):
        # Initialize the snake with a single segment at the center of the screen
        self.body = [pygame.Vector2(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2)]
        self.direction = pygame.Vector2(Config.SNAKE_SIZE, 0) # Initial direction: right
        self.next_direction = deque() # Queue to store pending direction changes
        self.growing = False # Flag to indicate if the snake should grow

    def move(self):
        # Update the snakes direction from the queue (if there are pending changes)
        if self.next_direction:
            next_direction = self.next_direction.popleft()
            # Prevent the snake from reversing direction
            if next_direction.x != -self.direction.x and next_direction.y != -self.direction.y:
                self.direction = next_direction

        # Move the snake by adding a new head segment in the current direction
        new_head = self.body[0] + self.direction
        self.body.insert(0 , new_head)

        # Remove the tail segment unless the snake is growing
        if not self.growing:
            self.body.pop()
        else:
            self.growing = False # Reset the growing flag

    def grow(self):
        # Set the growing flag to True so the snake grows when it moves
        self.growing = True

    def check_collision(self):
        # Check for collisions with the walls
        if (self.body[0].x < 0 or self.body[0].x >= Config.SCREEN_WIDTH 
            or
            self.body[0].y < 0 or self.body[0].y >= Config.SCREEN_HEIGHT):
            return True
        # Check for collisions with itself
        if self.body[0] in self.body[1:]:
            return True

        return False

    def draw(self, screen):
        # Draw each segment of the snake
        for segment in self.body:
            pygame.draw.rect(screen, (Config.GREEN), pygame.Rect(segment.x, segment.y, Config.SNAKE_SIZE, Config.SNAKE_SIZE))

class Food:
    def __init__(self, snake_body):
        # Initialize the food with a random position that doesnt overlap with the snake
        self.position = self.generate_position(snake_body)

    def generate_position(self, snake_body):
        # Generate a random position for the food that doesnt overlap with the snake
        while True:
            position = pygame.Vector2(
                random.randint(0, (Config.SCREEN_WIDTH - Config.FOOD_SIZE) // Config.FOOD_SIZE) * Config.FOOD_SIZE,
                random.randint(0 , (Config.SCREEN_HEIGHT - Config.FOOD_SIZE) // Config.FOOD_SIZE) * Config.FOOD_SIZE
            )
            if position not in snake_body:
                return position
            
    def respawn(self, snake_body):
        # Respawn the food at a new random position
        self.position = self.generate_position(snake_body)
    
    def draw(self, screen):
        # Draw the food on the screen
        pygame.draw.rect(screen, Config.RED, (self.position.x, self.position.y, Config.FOOD_SIZE, Config.FOOD_SIZE))

class GameManager:
    def __init__(self):
        # Initialize the game manager with a snake, food, score
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        self.paused = False
        self.game_state = "start" # Initial game state (start menu)
        
    def reset_game(self):
        # Reset the game to its initial state
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.game_over = False

    def load_high_score(self):
        # Load the high score from a file
        if os.path.exists(Config.HIGH_SCORE_FILE):
            with open(Config.HIGH_SCORE_FILE, "r") as file:
                content = file.read().strip()
                if content.isdigit():
                    return int(content)
        return 0
    
    def save_high_score(self):
        # Save the high score to a file
        with open(Config.HIGH_SCORE_FILE, "w") as file:
            file.write(str(self.high_score))

    def update(self):
        # Update the game state (move the snake, check for collisions)
        if self.game_state == "playing" and not self.paused and not self.game_over:
            self.snake.move()

            # Check if the snake has eaten the food
            if self.snake.body[0] == self.food.position:
                self.food.respawn(self.snake.body)
                self.snake.grow()
                self.score += 1

            # Check for collisions (game over if collision)
            if self.snake.check_collision():
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()

    def draw(self, screen):
        # Draw the current game state (start menu, playing, game over)
        screen.fill(Config.BLACK)

        if self.game_state == "start":
            # Draw the start menu
            font = pygame.font.Font(None, Config.FONT_TITLE_SIZE)
            title_text = font.render("Snake Game", True, Config.GREEN)
            screen.blit(title_text, (Config.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

            font = pygame.font.Font(None, Config.FONT_SIZE)
            start_text = font.render("Press SPACE to Start", True, Config.WHITE)
            screen.blit(start_text, (Config.SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
            quit_text = font.render("Press Q to Quit", True, Config.WHITE)
            screen.blit(quit_text, (Config.SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 350))
        
        elif self.game_state == "playing":
            # Draw the snake and food
            self.snake.draw(screen)
            self.food.draw(screen)

            # Draw the score and high score
            font = pygame.font.Font(None, Config.FONT_SIZE)
            score_text = font.render(f"Score: {self.score}", True, Config.WHITE)
            high_score_text = font.render(f"High Score: {self.high_score}", True, Config.WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(high_score_text, (10, 50))

            # Draw the message when paused
            if self.paused:
                paused_text = font.render("Paused! Press P to Resume", True, Config.WHITE)
                screen.blit(paused_text, (Config.SCREEN_WIDTH // 2 - paused_text.get_width() // 2, Config.SCREEN_HEIGHT // 2))

            # Draw the message when game over
            if self.game_over:
                game_over_text = font.render("Game over! Press R to Restart or Q to go to Menu", True, Config.WHITE)
                screen.blit(game_over_text, (Config.SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, Config.SCREEN_HEIGHT // 2))

        pygame.display.flip()


    def handle_events(self):
        # Handle user inputs (keyboard events)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == "start": # Start menu controlls
                    if event.key == pygame.K_SPACE: # Start the game
                        self.reset_game()
                        self.game_state = "playing"
                    elif event.key == pygame.K_q: # Quit the game
                        return False
        
                elif self.game_state == "playing": # Playing controlls
                    if self.game_over:
                        if event.key == pygame.K_r: # Restart the game
                            self.reset_game()
                            self.game_state = "playing"
                        elif event.key == pygame.K_q: # Back to menu
                            self.game_state = "start"
                    elif event.key == pygame.K_p: # Pause the game
                        self.paused = not self.paused
                    else:
                        if not self.paused:
                            # Handle direction changes (w/up, s/down, a/left, d/right)
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

# Set up the game window
screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

# Initialize the game clock and game manager
clock = pygame.time.Clock()
game_manager = GameManager()

# Main game loop
running = True
while running:
    running = game_manager.handle_events()
    game_manager.update()
    game_manager.draw(screen)
    pygame.display.flip()
    clock.tick(Config.FPS)

# Quit pygame and exit the program
pygame.quit()
sys.exit()