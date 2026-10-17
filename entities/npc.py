import math
import pygame
import core.settings as settings
from ui import UISequence, Dialogue
from world.tiles import InteractionTrigger
from core.utils import tile_to_pixel
  
class NPC(pygame.sprite.Sprite):
    def __init__(self, name: str, textures: dict, dialogue: list | str, obstacles: object, character_path: str = "assets/characters/dancing_star.png", pos: tuple = (0, 0), floating=True):
        super().__init__()
        self._layer = settings.LAYERS["npc"]
        
        pos = (tile_to_pixel(pos[0]), tile_to_pixel(pos[1]))
                
        # Create the texture and rect
        self.character_path = character_path
        self.image = textures["inactive"]
        self.rect = self.image.get_rect(topleft=pos)
        
        # Create a hitbox and put it at the characters feet
        self.hitbox = pygame.Rect(0, 0, 12, 8)
        self.hitbox.midbottom = self.rect.midbottom
        
        self.name = name
        self.dialogue = [dialogue] if isinstance(dialogue, str) else dialogue
        self.state = "IDLE"
        self.direction = "up"
        self.obstacles = obstacles
        
        self.trigger = InteractionTrigger(
            target=self,
            zone=self.rect.inflate(24, 24),
            keybind=pygame.K_e,
            keybind_text="E",
            text=f"Talk to {self.name}",
            textures=textures,
            on_trigger=self.interact
        )    
        
        self.floating = floating
        if self.floating:
            self.base_y = pos[1]
            self.amplitude = 1.5
            self.speed = 0.003
        
    def tick(self):
        if self.floating:
            offset = math.sin(pygame.time.get_ticks() * self.speed) * self.amplitude 
            self.rect.y = int(self.base_y + offset)
            
        self.trigger.zone.center = self.rect.center
    
    def interact(self):
        return UISequence(steps=[
            Dialogue(
                text=line,
                character_path=self.character_path,
                character_name=self.name
            )
            for line in self.dialogue
        ])
