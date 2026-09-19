import pygame
import settings
from utils import get_image, get_animation, flip_animation, tile_to_pixel

class Player(pygame.sprite.Sprite):
    def __init__(self, obstacles: object, pos: tuple = (0, 0)):
        super().__init__()
        
        self._layer = settings.LAYERS["player"]
        self.speed = 2
        self.state = "idle"
        self.direction = "down"
        self.frame_index = 0
        self.animation_speed = 0.2
        self.obstacles = obstacles
        try:
            pos = (tile_to_pixel(pos[0]), tile_to_pixel(pos[1]))
        except Exception:
            pos = (0, 0)

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

        # Create the texture and rect
        self.image = self.animations["idle_down"][0]
        self.rect = self.image.get_rect(topleft=pos)
        
        # Create a hitbox and put it at the characters feet
        self.hitbox = pygame.Rect(0, 0, 12, 6)
        self.hitbox.midbottom = self.rect.midbottom
        
    def tick(self):
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
        
        # Move the hitbox and the main rect
        self.hitbox.x += dx * self.speed
        self.hitbox.y += dy * self.speed
        
        # Check collisions and move character
        self.check_collisions()
        self.rect.midbottom = self.hitbox.midbottom
                
        # Change the frame
        frames = self.animations[f"{self.state}_{self.direction}"]
        if self.frame_index >= len(frames):
            self.frame_index = 0
        self.image = frames[int(self.frame_index)]
        
    def check_collisions(self):
        for obstacle in self.obstacles:
            obstacle_hitbox = getattr(obstacle, "hitbox", obstacle.rect)
            if self.hitbox.colliderect(obstacle_hitbox):
                if self.direction == "right":
                    self.hitbox.right = obstacle_hitbox.left
                elif self.direction == "left":
                    self.hitbox.left = obstacle_hitbox.right
                elif self.direction == "up":
                    self.hitbox.top = obstacle_hitbox.bottom
                elif self.direction == "down":
                    self.hitbox.bottom = obstacle_hitbox.top
                
                self.state = "idle"
                
    def set_pos(self, pos: tuple):
        pixel_x = tile_to_pixel(pos[0])
        pixel_y = tile_to_pixel(pos[1])
        self.rect.topleft = (pixel_x - 4, pixel_y) # apply offset for the player being 24x24 and the tiles 16x16 
        self.hitbox.midbottom = self.rect.midbottom
        if len(pos) > 2:
            self.direction = pos[2]

    def draw(self, screen):
        screen.blit(self.image, self.rect)