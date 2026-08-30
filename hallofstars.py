import sys
import pygame
import settings
from player import Player

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
        self.player = Player()
        
    def run(self):
        while self.running:
            # Quit check
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update Logic
            self.player.update()
        
            # Rendering
            self.display_surface.fill(settings.COLORS["background"])
            self.player.draw(screen=self.display_surface)
            
            scaled_surface = pygame.transform.scale(
                self.display_surface,
                (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
            )
            self.screen.blit(scaled_surface, (0, 0))
            
            pygame.display.flip()
            self.clock.tick(settings.FPS)
        
        pygame.quit()
        sys.exit()

            
            