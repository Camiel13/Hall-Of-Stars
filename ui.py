import pygame
import textwrap
from abc import ABC, abstractmethod

class UIElement(ABC):
    def __init__(self):
        self.is_finished = False
        self.value = None
    
    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass
    
    def start(self):
        pass

    def stop(self):
        pass

    def update(self):
        pass
    
    def _draw_background_blur(self, surface: pygame.Surface, alpha: int = 170):
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))
        
    def _draw_box(
        self, 
        surface: pygame.Surface, 
        rect: pygame.Rect, 
        bg_color: tuple[int, int, int],
        border_color: tuple[int, int, int],
        border_width = 5,
        border_radius: int = 12
    ):
        pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=border_radius)
        
    def _draw_text(
        self,
        surface: pygame.Surface, 
        font: pygame.font.Font,
        text: str,
        color: tuple[int, int, int],
        **rect_kwargs
    ):
        surf = font.render(text, True, color)
        rect = surf.get_rect(**rect_kwargs)
        surface.blit(surf, rect)
        return rect

class InputScreen(UIElement):
    def __init__(self, placeholder: str = "Enter text here...", question: str = "Input your answer...", key: str = None):
        super().__init__()
        self.value = ""
        self.key = key
        self.placeholder = placeholder
        self.question = question

        # Font
        self.font = pygame.font.SysFont("p052", 45, bold=True)
        self.placeholder_font = pygame.font.SysFont("sans-sarif", 20)
        self.input_font = pygame.font.SysFont("tinos", 20)
        
        # Colors
        self.bg_color = (248, 248, 248)
        self.question_color = (248, 224, 96)
        self.input_color = (18, 11, 21)
        self.placeholder_color = (178, 183, 198)
        self.border_color = (232, 224, 176)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.value:
                    self.value = self.value.strip()
                    self.is_finished = True
            elif event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            else:
                if len(self.value) < 30 and (event.unicode.isalnum() or event.unicode in "_"):
                    self.value += event.unicode
    
    def draw(self, surface: pygame.Surface):
        # Draw blur
        self._draw_background_blur(surface=surface)
        
        # Draw the rect
        input_field = pygame.Rect(0, 0, 400, 50)
        input_field.center = (surface.get_width() // 2, (surface.get_height() // 2) + 40)
        self._draw_box(surface=surface, rect=input_field, bg_color=self.bg_color, border_color=self.border_color)
        
        # Add the question
        self._draw_text(surface=surface, font=self.font, text=self.question, color=self.question_color, center=(surface.get_width() // 2, (surface.get_height() // 2) - 40))
        
        # Render typed text or placeholder
        if self.value:
            text_surface = self.placeholder_font.render(self.value, True, self.input_color)
        else:
            text_surface = self.placeholder_font.render(self.placeholder, True, self.placeholder_color)
            
        # Center the text
        text_rect = text_surface.get_rect(midleft=(input_field.x + 12, input_field.centery))
        surface.blit(text_surface, text_rect)
        
class Dialogue(UIElement):
    def __init__(self, text: str, character_path: pygame.Surface = None, character_name: str = None):
        super().__init__()
        self.text = text
        self.character_name = character_name
        self.sound = pygame.mixer.Sound("assets/audio/cartoon-yap.mp3")
        
        if character_path:
            raw_image = pygame.image.load(character_path)
            target_height = 168
            aspect_ratio = raw_image.get_width() / raw_image.get_height()
            target_width = int(target_height * aspect_ratio)
            self.character_sprite = pygame.transform.scale(raw_image, (target_width, target_height))
                
        # Colors
        self.bg_color = (232, 224, 176)
        self.text_color = (18, 11, 21)
        self.border_color = (248, 224, 96)
        
        # Fonts
        self.font = pygame.font.SysFont("z003", 25)
        self.name_font = pygame.font.SysFont("z003", 25, italic=True)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
            if self.is_talking:
                self.visible_characters = len(self.text)
                self.is_talking = False
                self.sound.stop()
            else:
                self.is_finished = True
    
    def draw(self, surface: pygame.Surface):
        # Create the background box
        box = pygame.Rect(0, 0, surface.get_width() // 2, surface.get_height() // 2)
        box.center = (surface.get_width() // 2, surface.get_height() // 2)

        # Draw blur
        self._draw_background_blur(surface=surface)
        
        # Draw box and border
        self._draw_box(surface=surface, rect=box, bg_color=self.bg_color, border_color=self.border_color)
        
        # Draw the character sprite if present
        character_padding = 50
        if self.character_sprite:
            character = self.character_sprite.get_rect(
                bottomleft=(0 + character_padding, surface.get_height() - character_padding)
            )
            surface.blit(self.character_sprite, character)
            
        # Write text
        line_height = 35
        start_x, start_y = box.x + 32, box.y + 32
        
        remaining = self.visible_characters
        for i, line in enumerate(self.lines):
            if remaining <= 0:
                break

            chars_to_show = min(len(line), remaining)
            text_surf = self.font.render(line[:chars_to_show], True, self.text_color)
            surface.blit(text_surf, (start_x, start_y + (i * line_height)))
            
            remaining -= len(line) + 1
            
        if self.character_name:
            name_surf = self.name_font.render(f"~ {self.character_name} ", True, self.text_color)
            name_rect = name_surf.get_rect(bottomleft=(box.left + 35, box.bottom - 35))
            surface.blit(name_surf, name_rect)
         
    def update(self):
        if self.is_talking:
            if self.visible_characters < len(self.text):
                self.visible_characters += 1
            else:
                self.is_talking = False
                self.sound.stop()       
            
    def start(self):
        self.visible_characters = 0
        self.is_talking = True
        self.sound.play(loops=-1)
        self.lines = textwrap.wrap(self.text, width=48)
    
    def stop(self):
        self.is_talking = False
        self.sound.stop()      

class UISequence:
    def __init__(self, steps: list[UIElement]):
        self.steps = steps
        self.current_index = 0
        self.is_finished = False
        self.results = {}
        
        if self.steps:
            self.current_step.start()

    @property
    def current_step(self):
        return self.steps[self.current_index]
        
    def handle_event(self, event) -> str | None:
        if self.is_finished:
            return

        # Let the current step handle the input event
        self.current_step.handle_event(event=event)
        
        if self.current_step.is_finished:
            self.current_step.stop()
            
            if self.current_step.value and getattr(self.current_step, "key", None):
                self.results[self.current_step.key] = self.current_step.value
                
            self.current_index += 1
            if self.current_index >= len(self.steps):
                self.is_finished = True
            else:
                self.current_step.start()
                
    def draw(self, surface: pygame.Surface):
        if not self.is_finished:
            self.current_step.draw(surface=surface)
    
    def update(self):
        if not self.is_finished:
            self.current_step.update()



def create_welcome_sequence() -> UISequence:
    return UISequence(
        steps=[
            Dialogue(
                text="Welcome to The Hall of Stars. You can move with WASD or Arrow Keys. Doors automatically bring you into the new room. You can interact with NPC's with 'E'. Use 'Space' or 'Enter' to navigate to the next page.",
                character_path="assets/characters/standing_star.png",
                character_name="Starling"
            ),
            Dialogue(
                text="Hall of Stars is an interactive hall where you can explore all your stardance projects. Each door represents a project of yours on the biggest Hack Club YSWS event yet: Stardance.",
                character_path="assets/logo/star_with_flag.png",
                character_name="Starling"
            ),
            InputScreen(
                placeholder="Enter your username...",
                question="What is your username on Stardance?",
                key="username"
            ),
            Dialogue(
                text="Time to wander around the Hall of Stars... Have fun!",
                character_path="assets/characters/dancing_star.png",
                character_name="Starling"
            ),
        ]
    )