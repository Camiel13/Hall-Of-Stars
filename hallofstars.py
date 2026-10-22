import sys
import pygame
import core.settings as settings
from world.level import Level
from ui import UISequence, create_welcome_sequence, UIManager

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
        
        self.show_loading_screen()
        
        # Create the world
        self.ui_manager = UIManager()
        self.level = Level(display_surface=self.display_surface, ui_manager=self.ui_manager)
        if not self.level.api.stardance_username:
            self.ui_manager.set_ui(create_welcome_sequence(), self.on_welcome_finish)
        
    def run(self):
        while self.running:
            # Quit check
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Pass the event to the UI manager
                self.ui_manager.handle_event(event)
                        
            # Tick Logic
            if not self.ui_manager.active_ui:
                self.level.tick()
            
        
            # Rendering
            self.display_surface.fill(settings.COLORS["background"])
            self.level.draw()
            
            scaled_surface = pygame.transform.scale(
                self.display_surface,
                (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
            )
            self.screen.blit(scaled_surface, (0, 0))
            
            if self.ui_manager.active_ui or self.ui_manager.overlay:
                self.ui_manager.update()
                self.ui_manager.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(settings.FPS)
        
        pygame.quit()
        sys.exit()
        
    def show_loading_screen(self):
        loading_screen = pygame.image.load("assets/backgrounds/ship_bg.png").convert()
        self.screen.blit(loading_screen, (0, 0))
        pygame.display.flip()
        pygame.event.pump()
            
    def on_welcome_finish(self, ui_sequence):
        self.level.api.set_username(ui_sequence.results["username"])
        self.level.hallway.unload(camera=self.level.camera_group, obstacles=self.level.obstacles)
        self.level.generate_hallway()