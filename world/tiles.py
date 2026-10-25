import math
import pygame
import core.settings as settings

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surface, layer=settings.LAYERS["decoration"], hitbox: pygame.Rect = None):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = hitbox if hitbox is not None else self.rect
        self._layer = layer

class Door(Tile):
    def __init__(self, pos, surface, target_room=None, target_pos=None, layer=settings.LAYERS["door"], hitbox=None):
        hitbox = hitbox if hitbox is not None else pygame.Rect(pos[0], pos[1], 16, 18)
        super().__init__(pos=pos, surface=surface, layer=layer, hitbox=hitbox)
        self.target_room = target_room
        self.target_pos = target_pos

class FloatingTile(Tile):
    def __init__(self, pos, surface, layer=settings.LAYERS["door"], hitbox=None, amplitude=2, animation_speed=0.006):
        super().__init__(pos=pos, surface=surface, layer=layer, hitbox=hitbox)
        self.base_y = pos[1]
        self.amplitude = amplitude
        self.speed = animation_speed
        
    def tick(self):
        offset = math.sin(pygame.time.get_ticks() * self.speed) * self.amplitude
        self.rect.y = int(self.base_y + offset)

class InteractionTrigger:
    def __init__(self, target, zone, keybind, keybind_text, text, textures: dict = None, on_trigger=None, layer=settings.LAYERS["decoration"]):
        self.zone = zone
        self.target = target
        self.keybind = keybind
        self.keybind_text = keybind_text
        self.text = text
        self.on_trigger = on_trigger
        self.textures = textures or {}
        self.active = False

    def tick(self, player):
        self.active = player.hitbox.colliderect(self.zone)
        if self.textures and hasattr(self.target, "image"):
            self.target.image = self.textures["active" if self.active else "inactive"]
