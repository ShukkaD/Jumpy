import pygame
import random
import os
import sys
from pygame import mixer
from spritesheet import SpriteSheet
from enemy import Enemy
import encrypt
from encrypt import Encrypt
from encrypt import Decrypt

import os
import pygame
from pygame import mixer
import random
import sys

# Initialize the mixer and pygame
mixer.init()
pygame.init()

# Set screen dimensions
screen_width = 400
screen_height = 600

# Set up the screen
scrsize = (screen_width, screen_height)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Jumpy')

# Initialize clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Get the base directory
base_dir = os.path.dirname(__file__)

# Load assets with the new path approach
pygame.mixer.music.load(os.path.join(base_dir, 'Assets/music.mp3'))
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1, 0.0)

jump_fx = pygame.mixer.Sound(os.path.join(base_dir, 'Assets/jump.mp3'))
jump_fx.set_volume(0.5)

death_fx = pygame.mixer.Sound(os.path.join(base_dir, 'Assets/death.mp3'))
death_fx.set_volume(0.5)

# Game variables
gravity = 1
max_platforms = 10
scroll_thresh = 200
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

# Check for high score file and read it
if os.path.exists(os.path.join(base_dir, 'best.json')):
    with open(os.path.join(base_dir, 'best.json'), 'r') as file:
        Decrypt(os.path.join(base_dir, 'best.json'), 'key')
        high_score = int(file.read())
else:
    high_score = 0

high_score_prev = high_score
white = (255, 255, 255)
black = (0, 0, 0)
panel_color = (153, 217, 234)
high_score_color = (21, 34, 56)

# Load fonts
font_small = pygame.font.Font(os.path.join(base_dir, 'Assets/game_over.ttf'), 20)
font_small_by_a_bit = pygame.font.Font(os.path.join(base_dir, 'Assets/game_over.ttf'), 18)
font_large = pygame.font.Font(os.path.join(base_dir, 'Assets/game_over.ttf'), 24)
font_extrasmall = pygame.font.Font(os.path.join(base_dir, 'Assets/game_over.ttf'), 14)
font_extra_extrasmall = pygame.font.Font(os.path.join(base_dir, 'Assets/game_over.ttf'), 10)

# Load images
jumpy_image = pygame.image.load(os.path.join(base_dir, 'Assets/jumpy.png')).convert_alpha()

start_image = pygame.image.load(os.path.join(base_dir, 'Assets/jumpy.png')).convert_alpha()
start_image = pygame.transform.scale(start_image, (200, 200)).convert_alpha()

bg_image = pygame.image.load(os.path.join(base_dir, 'Assets/bg.png'))
bg_image = pygame.transform.scale(bg_image, scrsize).convert_alpha()

platform_image = pygame.image.load(os.path.join(base_dir, 'Assets/wood.png')).convert_alpha()

bird_sheet_path = os.path.join(base_dir, 'Assets/bird.png')
bird_sheet = SpriteSheet(bird_sheet_path)


# Function to draw text
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


# Function to draw the score panel
def draw_score_panel():
    pygame.draw.rect(screen, panel_color, (0, 0, screen_width, 30))
    draw_text('SCORE: ' + str(score), font_extra_extrasmall, white, 5, 7)
    draw_text('CURRENT HIGH SCORE: ' + str(high_score), font_extra_extrasmall, white, screen_width - 250, 7)


# Function to draw the background
def draw_bg(bg_scroll):
    screen.blit(bg_image, (0, 0 + bg_scroll))
    screen.blit(bg_image, (0, -screen_height + bg_scroll))


# Class for Line
class Line(pygame.sprite.Sprite):
    def __init__(self, surface, color, start_x, y, end_x, thickness):
        super().__init__()
        self.surface = surface
        self.color = color
        self.start_x = start_x
        self.y = y
        self.end_x = end_x
        self.thickness = thickness
        pygame.draw.line(self.surface, self.color, (self.start_x, self.y), (self.end_x, self.y), self.thickness)


# Start menu
startmenu = True
while startmenu:
    draw_bg(bg_scroll)
    draw_text('PRESS SPACE TO BEGIN', font_small_by_a_bit, high_score_color, 18, screen_height / 2 - 100)
    screen.blit(start_image, (screen_width / 2 - 105, screen_height - 250))
    pygame.display.flip()
    key = pygame.key.get_pressed()
    if key[pygame.K_SPACE] or key[pygame.K_RETURN]:
        startmenu = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Encrypt(os.path.join(base_dir, 'best.json'))
            pygame.quit()
            sys.exit()


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(jumpy_image, (45, 45))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False

    def move(self):
        scroll = 0
        dx = 0
        dy = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx = -10
            self.flip = True
        if key[pygame.K_LEFT]:
            dx = -10
            self.flip = True
        if key[pygame.K_d]:
            dx = 10
            self.flip = False
        if key[pygame.K_RIGHT]:
            dx = 10
            self.flip = False
        self.vel_y += gravity
        dy += self.vel_y

        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20
                        jump_fx.play()

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right

        if self.rect.top <= scroll_thresh:
            if self.vel_y < 0:
                scroll = -dy

        self.rect.x += dx
        self.rect.y += dy + scroll

        self.mask = pygame.mask.from_surface(self.image)

        return scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))


# Create player
jumpy = Player(screen_width // 2, screen_height - 150)


# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        super().__init__()
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        if self.moving:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > screen_width:
            self.direction *= -1
            self.move_counter = random.randint(0, 50)

        self.rect.y += scroll

        if self.rect.top > screen_height:
            self.kill()


# Create platform and enemy groups
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

platform = Platform(screen_width / 2 - 28, screen_height - 25, 50, False)
platform_group.add(platform)

# Main game loop
run = True
while run:
    clock.tick(FPS)

    if not game_over:
        scroll = jumpy.move()

        bg_scroll += scroll
        if bg_scroll >= screen_height:
            bg_scroll = 0
        draw_bg(bg_scroll)

        if len(platform_group) < max_platforms:
            p_w = random.randint(40, 60)
            p_x = random.randint(0, screen_width - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            p_type = random.randint(1, 2)
            p_moving = p_type == 1 and score >= 3000
            platform = Platform(p_x, p_y, p_w, p_moving)
            platform_group.add(platform)

        platform_group.update(scroll)

        if len(enemy_group) == 0 and score > 1500:
            enemy = Enemy(screen_width, random.randint(75, 150), bird_sheet, 1.5)
            enemy_group.add(enemy)

        enemy_group.update(scroll, screen_width)

        if scroll > 0:
            score += scroll

        if score > high_score:
            high_score = score
            if os.path.exists(os.path.join(base_dir, 'best.json')):
                os.remove(os.path.join(base_dir, 'best.json'))
            with open(os.path.join(base_dir, 'best.json'), 'w') as file:
                file.write(str(high_score))

        high_score_line = Line(screen, white, 0, score - high_score_prev + scroll_thresh, screen_width, 3)
        draw_text('HIGH SCORE', font_extrasmall, high_score_color, screen_width - 300,
                  score - high_score_prev + scroll_thresh + 5)

        platform_group.draw(screen)
        enemy_group.draw(screen)
        jumpy.draw()

        draw_score_panel()

        if jumpy.rect.top > screen_height:
            game_over = True
            death_fx.play()

        if pygame.sprite.spritecollide(jumpy, enemy_group, False):
            if pygame.sprite.spritecollide(jumpy, enemy_group, False, pygame.sprite.collide_mask):
                game_over = True
                death_fx.play()
    else:
        if score > high_score:
            high_score = score
            if os.path.exists(os.path.join(base_dir, 'best.json')):
                os.remove(os.path.join(base_dir, 'best.json'))
            with open(os.path.join(base_dir, 'best.json'), 'w') as file:
                file.write(str(high_score))

        if fade_counter < screen_width:
            fade_counter += 5
            for y in range(0, 6, 2):
                pygame.draw.rect(screen, black, (0, y * 100, fade_counter, screen_height / 6))
                pygame.draw.rect(screen, black,
                                 (screen_width - fade_counter, (y + 1) * 100, screen_width, screen_height / 6))

        else:
            draw_text('GAME OVER!', font_large, white, 80, 200)
            draw_text('SCORE: ' + str(score), font_large, white, 75, 250)
            draw_text('HIGH SCORE: ' + str(high_score), font_small, white, 45, 300)
            draw_text('PRESS SPACE TO PLAY AGAIN', font_extrasmall, white, 21, 350)

        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] or key[pygame.K_RETURN]:
            game_over = False
            score = 0
            scroll = 0
            bg_scroll = 0
            fade_counter = 0
            high_score_prev = high_score
            jumpy.rect.center = (screen_width // 2, screen_height - 150)
            enemy_group.empty()
            platform_group.empty()
            platform = Platform(screen_width / 2 - 28, screen_height - 25, 50, False)
            platform_group.add(platform)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if score > high_score:
                high_score = score
                if os.path.exists(os.path.join(base_dir, 'best.json')):
                    os.remove(os.path.join(base_dir, 'best.json'))
                with open(os.path.join(base_dir, 'best.json'), 'w') as file:
                    file.write(str(high_score))
            run = False

    pygame.display.update()

Encrypt(os.path.join(base_dir, 'best.json'))
pygame.quit()
