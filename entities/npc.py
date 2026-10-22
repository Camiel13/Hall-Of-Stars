import math
import pygame
import random
import core.settings as settings
from ui import UISequence, Dialogue
from core.utils import tile_to_pixel
from world.tiles import InteractionTrigger
  
class NPC(pygame.sprite.Sprite):
    def __init__(self, name: str, textures: dict, dialogue: list | str, project_data: dict, obstacles: object, character_path: str = "assets/characters/dancing_star.png", pos: tuple = (0, 0), max_wander_distance: int = 72, floating=True):
        super().__init__()
        self._layer = settings.LAYERS["npc"]
        self.project_data = project_data
        
        self.spawn_x = tile_to_pixel(pos[0])
        self.spawn_y = tile_to_pixel(pos[1])
        self.max_wander_distance = max_wander_distance
                
        # Create the texture and rect
        self.character_path = character_path
        self.image = textures["inactive"]
        self.rect = self.image.get_rect(topleft=(self.spawn_x, self.spawn_y))
        
        # Create a hitbox and put it at the characters feet
        self.hitbox = pygame.Rect(0, 0, 12, 8)
        self.hitbox.midbottom = self.rect.midbottom
        
        self.name = name
        self.dialogue = [dialogue] if isinstance(dialogue, str) else dialogue
        self.speed = 1
        self.state = "IDLE"
        self.direction = "up"
        self.obstacles = obstacles
        self.timer = random.randint(60, 180)
        
        self.trigger = InteractionTrigger(
            target=self,
            zone=self.rect.inflate(16, 16),
            keybind=pygame.K_e,
            keybind_text="E",
            text=f"Talk to {self.name}",
            textures=textures,
            on_trigger=self.interact
        )    
        
        self.floating = floating
        if self.floating:
            self.amplitude = 1.5
            self.float_speed = 0.005
        
    def tick(self):
        # Move the image to the hitbox
        self.rect.midbottom = self.hitbox.midbottom
        
        # Floating animation
        if self.floating:
            offset = math.sin(pygame.time.get_ticks() * self.float_speed) * self.amplitude 
            self.rect.y += int(offset)
            
        # Move interaction zone onto the NPC
        self.trigger.zone.center = self.rect.center
    
        # Wandering logic
        self.timer -= 1
        if self.timer <= 0:
            if self.state == "IDLE":
                self.state = "WANDER"
                
                diff_x = self.hitbox.centerx - self.spawn_x
                diff_y = self.hitbox.centery - self.spawn_y
                
                if abs(diff_x) > self.max_wander_distance:
                    self.direction = "left" if diff_x > 0 else "right"
                elif abs(diff_y) > self.max_wander_distance:
                    self.direction = "up" if diff_y > 0 else "down"
                else:
                    self.direction = random.choice(["up", "down", "left", "right"])
                
                self.timer = random.randint(15, 28)
            else:
                self.state = "IDLE"
                self.timer = random.randint(90, 320)
                
        dx = 0
        dy = 0
        if self.state == "WANDER":
            if self.direction == "right": dx = 1
            if self.direction == "left": dx = -1
            if self.direction == "down": dy = 1
            if self.direction == "up": dy = -1
                    
        self.hitbox.x += dx * self.speed
        self.hitbox.y += dy * self.speed
        self.check_collisions()
        
    def check_collisions(self):
        for obstacle in self.obstacles:
            obstacle_hitbox = getattr(obstacle, "hitbox", obstacle.rect)
            if self.hitbox.colliderect(obstacle_hitbox):
                opposite = {
                    "up": "down",
                    "down": "up",
                    "right": "left",
                    "left": "right",
                }
                
                if self.direction == "right":
                    self.hitbox.right = obstacle_hitbox.left
                elif self.direction == "left":
                    self.hitbox.left = obstacle_hitbox.right
                elif self.direction == "up":
                    self.hitbox.top = obstacle_hitbox.bottom
                elif self.direction == "down":
                    self.hitbox.bottom = obstacle_hitbox.top
                
                self.direction = opposite[self.direction]
                self.state = "IDLE"
                self.timer = random.randint(30, 90)
    
    def interact(self):
        return UISequence(steps=[
            Dialogue(
                text=line,
                character_path=self.character_path,
                character_name=self.name
            )
            for line in self.dialogue
        ])
