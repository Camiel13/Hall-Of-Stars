import pygame
import settings
from utils import get_image, get_animation, flip_animation

class Player(pygame.sprite.Sprite):
    def __init__(self, pos: tuple = (0, 0)):
        super().__init__()
        
        self._layer = settings.LAYERS["player"]
        self.speed = 2
        self.state = "idle"
        self.direction = "down"
        self.frame_index = 0
        self.animation_speed = 0.2

        idle_sheet = pygame.image.load("assets/player/idle-sheet.png").convert_alpha()
        walk_sheet = pygame.image.load("assets/player/walk-sheet.png").convert_alpha()
        
        self.animations = {
            "idle_down": get_animation(sheet=idle_sheet, start_frame=0, count=4),
            "idle_right": get_animation(sheet=idle_sheet, start_frame=4, count=4),
            "idle_left": flip_animation(get_animation(sheet=idle_sheet, start_frame=4, count=4)),
            "idle_up": get_animation(sheet=idle_sheet, start_frame=8, count=4),
            
            "walk_down": get_animation(sheet=walk_sheet, start_frame=0, count=4),
            "walk_right": get_animation(sheet=walk_sheet, start_frame=4, count=4),
            "walk_left": flip_animation(get_animation(sheet=walk_sheet, start_frame=4, count=4)),
            "walk_up": get_animation(sheet=walk_sheet, start_frame=8, count=4)
        }

        self.image = self.animations["idle_down"][0]
        self.rect = self.image.get_rect(topleft=pos)
        
    def update(self):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        
        # Check all direction, order matters for the 'retro' up, down, left or right vibe
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction = "up"
            dy -= 1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction = "down"
            dy += 1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction = "right"
            dx += 1
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction = "left"
            dx -= 1 
        
        self.state = "walk" if dx or dy else "idle"
        self.frame_index += self.animation_speed 
        
        # Move the position
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        # Change the frame
        frames = self.animations[f"{self.state}_{self.direction}"]
        if self.frame_index >= len(frames):
            self.frame_index = 0
        self.image = frames[int(self.frame_index)]
        
        print(self.rect.x, self.rect.y)
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)