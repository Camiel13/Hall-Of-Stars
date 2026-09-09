import sys
import pygame
import settings
from api import API
from level import Level
from player import Player
from camera import CameraGroup

class Game:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        )
        self.display_surface = pygame.Surface(
            (settings.INTERNAL_WIDTH, settings.INTERNAL_HEIGHT)
        )
        
        pygame.display.set_caption("Hall of Stars")
        self.clock = pygame.time.Clock()
        self.running = True
        self.api = API()
        
        # Define the sprites and add them to the camera
        self.player = Player()
        self.camera_group = CameraGroup(display_surface=self.display_surface)
        self.camera_group.add(self.player)
        self.level = Level(camera=self.camera_group, api=self.api)
        
    def run(self):
        while self.running:
            # Quit check
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update Logic
            self.update()
        
            # Rendering
            self.display_surface.fill(settings.COLORS["background"])
            self.camera_group.draw_sprites(target=self.player)
            
            scaled_surface = pygame.transform.scale(
                self.display_surface,
                (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
            )
            self.screen.blit(scaled_surface, (0, 0))
            
            pygame.display.flip()
            self.clock.tick(settings.FPS)
        
        pygame.quit()
        sys.exit()
        
    def update(self):
        self.player.update()