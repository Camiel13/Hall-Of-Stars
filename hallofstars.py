import sys
import pygame
import settings
from level import Level
from ui import WelcomeScreen, Dialogue

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
        
        # Create the world
        self.level = Level(display_surface=self.display_surface)
        self.state = "PLAYING" if self.level.api.stardance_username else "WELCOMING"
        self.welcome_screen = None
        if self.state == "WELCOMING":
            self.welcome_screen = WelcomeScreen()
        
    def run(self):
        while self.running:
            # Quit check
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.state == "WELCOMING":
                    self.welcome_screen.handle_event(event)
                    if self.welcome_screen.is_finished:
                        self.state = "PLAYING"                        
                        self.level.api.set_username(self.welcome_screen.username)
                        self.level.hallway.unload(camera=self.level.camera_group, obstacles=self.level.obstacles)
                        self.level.generate_hallway()
                        self.welcome_screen = None
                        
            # Tick Logic
            if self.state == "PLAYING":
                self.level.tick()
        
            # Rendering
            self.display_surface.fill(settings.COLORS["background"])
            self.level.draw()
            
            scaled_surface = pygame.transform.scale(
                self.display_surface,
                (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
            )
            self.screen.blit(scaled_surface, (0, 0))
            
            if self.state == "WELCOMING":
                self.welcome_screen.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(settings.FPS)
        
        pygame.quit()
        sys.exit()