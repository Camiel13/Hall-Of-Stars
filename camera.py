import pygame
import settings

class CameraGroup(pygame.sprite.LayeredUpdates):
    def __init__(self, display_surface):
        super().__init__()
        
        self.offset = pygame.math.Vector2(0, 0)
        self.display_surface = display_surface
        
        self.half_width = settings.INTERNAL_WIDTH // 2
        self.half_height = settings.INTERNAL_HEIGHT // 2

    def draw_sprites(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height
        
        # sorting for later: key=lambda x: x.rect.centery
        for sprite in self.sprites():
            # Position = World Position - Camera Offset
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)