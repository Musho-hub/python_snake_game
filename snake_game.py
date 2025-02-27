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
        # print("Checking for collision:", self.body[0]) # Debbuging
        # Wall collision
        if (self.body[0].x < 0 or self.body[0].x >= Config.SCREEN_WIDTH 
            or
            self.body[0].y < 0 or self.body[0].y >= Config.SCREEN_HEIGHT):
            # print("Wall collision detected!") # Debugging
            return True
        # Self collision
        if self.body[0] in self.body[1:]:
            # print("Self collision detected!") # Debugging
            return True

        return False

    def draw(self, screen):
        for segment in self.body:
            pygame.draw.rect(screen, (Config.GREEN), pygame.Rect(segment.x, segment.y, Config.SNAKE_SIZE, Config.SNAKE_SIZE))

class Food:
    def __init__(self, snake_body):
        self.position = self.generate_position(snake_body)

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
    
    def draw(self, screen):
        pygame.draw.rect(screen, Config.RED, (self.position.x, self.position.y, Config.FOOD_SIZE, Config.FOOD_SIZE))

class GameManager:
    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        self.paused = False
        self.game_state = "start"
        
    def reset_game(self):
        self.snake = Snake()
        # print("Snake starting position", self.snake.body) # Debugging
        self.food = Food(self.snake.body)
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
        if self.game_state == "playing" and not self.paused and not self.game_over:
            self.snake.move()

            if self.snake.body[0] == self.food.position:
                self.food.respawn(self.snake.body)
                self.snake.grow()
                self.score += 1

            if self.snake.check_collision():
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()

    def draw(self, screen):
        screen.fill(Config.BLACK)

        if self.game_state == "start":
            font = pygame.font.Font(None, Config.FONT_TITLE_SIZE)
            title_text = font.render("Snake Game", True, Config.GREEN)
            screen.blit(title_text, (Config.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

            font = pygame.font.Font(None, Config.FONT_SIZE)
            start_text = font.render("Press SPACE to Start", True, Config.WHITE)
            screen.blit(start_text, (Config.SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
            quit_text = font.render("Press Q to Quit", True, Config.WHITE)
            screen.blit(quit_text, (Config.SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 350))
        
        elif self.game_state == "playing":
            self.snake.draw(screen)
            self.food.draw(screen)

            font = pygame.font.Font(None, Config.FONT_SIZE)
            score_text = font.render(f"Score: {self.score}", True, Config.WHITE)
            high_score_text = font.render(f"High Score: {self.high_score}", True, Config.WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(high_score_text, (10, 50))

            if self.paused:
                paused_text = font.render("Paused! Press P to Resume", True, Config.WHITE)
                screen.blit(paused_text, (Config.SCREEN_WIDTH // 2 - paused_text.get_width() // 2, Config.SCREEN_HEIGHT // 2))
        
            if self.game_over:
                game_over_text = font.render("Game over! Press R to Restart or Q to Quit", True, Config.WHITE)
                screen.blit(game_over_text, (Config.SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, Config.SCREEN_HEIGHT // 2))

        pygame.display.flip()


    def handle_events(self):
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
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.game_state = "playing"
                        elif event.key == pygame.K_q: # Back to menu
                            self.game_state = "start"
                    elif event.key == pygame.K_p: # Pause
                        self.paused = not self.paused
                    else:
                        if not self.paused:
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

screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()
game_manager = GameManager()

running = True
while running:
    running = game_manager.handle_events()
    game_manager.update()
    game_manager.draw(screen)
    pygame.display.flip()
    clock.tick(Config.FPS)

# Quit pygame
pygame.quit()
sys.exit()