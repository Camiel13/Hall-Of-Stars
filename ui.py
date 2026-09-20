import pygame
import textwrap

class InputBox:
    def __init__(self, placeholder: str = "Enter text here...", question: str = "Input your answer..."):
        self.value = ""
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
        
    def handle_event(self, event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return self.value.strip()
            elif event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            else:
                if len(self.value) < 30 and (event.unicode.isalnum() or event.unicode in "_"):
                    self.value += event.unicode
    
    def draw(self, surface: pygame.Surface):
        # Draw blur
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))
        
        # Draw the rect
        input_field = pygame.Rect(0, 0, 400, 50)
        input_field.center = (surface.get_width() // 2, (surface.get_height() // 2) + 40)
        pygame.draw.rect(surface, self.bg_color, input_field, border_radius=10)
        pygame.draw.rect(surface, self.border_color, input_field, width=5, border_radius=10)
        
        # Add the question
        question_surf = self.font.render(self.question, True, self.question_color)
        question_rect = question_surf.get_rect(center=(surface.get_width() // 2, (surface.get_height() // 2) - 40))
        surface.blit(question_surf, question_rect)
        
        # Render typed text or placeholder
        if self.value:
            text_surface = self.placeholder_font.render(self.value, True, self.input_color)
        else:
            text_surface = self.placeholder_font.render(self.placeholder, True, self.placeholder_color)
            
        # Center the text
        text_rect = text_surface.get_rect(midleft=(input_field.x + 12, input_field.centery))
        surface.blit(text_surface, text_rect)
        
class Dialogue:
    def __init__(self, text: str, character_path: pygame.Surface = None, character_name: str = None):
        self.text = text
        self.character_sprite = pygame.image.load(character_path).convert_alpha()
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
        
    def start(self):
        self.visible_characters = 0
        self.is_talking = True
        self.sound.play(loops=-1)
        self.lines = textwrap.wrap(self.text, width=48)
        
    def update(self):
        if self.is_talking:
            if self.visible_characters < len(self.text):
                self.visible_characters += 1
            else:
                self.is_talking = False
                self.sound.stop()
        
    
    def draw(self, surface: pygame.Surface):
        # Create the background box
        box_width = surface.get_width() // 2
        box_height = surface.get_height() // 2
        self.box = pygame.Rect(0, 0, box_width, box_height)
        self.box.center = (surface.get_width() // 2, surface.get_height() // 2)

        # Draw blur
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))
        
        # Draw box and border
        pygame.draw.rect(surface, self.bg_color, self.box, border_radius=12)
        pygame.draw.rect(surface, self.border_color, self.box, width=5, border_radius=12)
        
        # Draw the character sprite if present
        character_padding = 50
        if self.character_sprite:
            character = self.character_sprite.get_rect(
                bottomleft=(0 + character_padding, surface.get_height() - character_padding)
            )
            surface.blit(self.character_sprite, character)
            
        # Write text
        line_height = 35
        start_x, start_y = self.box.x + 32, self.box.y + 32
        
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
            name_rect = name_surf.get_rect(bottomleft=(self.box.left + 35, self.box.bottom - 35))
            surface.blit(name_surf, name_rect)
            
        self.update()
    
    def stop(self):
        self.is_talking = False
        self.sound.stop()        

class WelcomeScreen:
    def __init__(self):
        self.pages = [
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
            InputBox(
                placeholder="Enter your username...",
                question="What is your username on Stardance?"
            ),
            Dialogue(
                text="Time to wander around the Hall of Stars username... Have fun!",
                character_path="assets/characters/dancing_star.png",
                character_name="Starling"
            ),
        ]
        self.pages[0].start()
        self.current_page = 0
        self.is_finished = False
        self.username = ""
        
    def handle_event(self, event) -> str | None:
        if self.current_page == 0:
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                self.current_page = 1
                self.pages[0].stop()
                self.pages[1].start()
        elif self.current_page == 1:    
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                self.current_page = 2
                self.pages[1].stop()
        elif self.current_page == 2:
            input_box = self.pages[2]
            entered_username = input_box.handle_event(event)
            if entered_username:
                self.username = entered_username
                self.current_page = 3
                self.pages[3].text = self.pages[3].text.replace("username", entered_username)
                self.pages[3].start()
        elif self.current_page == 3:
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                self.pages[3].stop()
                self.is_finished = True
                
    def draw(self, surface: pygame.Surface):
        current_component = self.pages[self.current_page]
        current_component.draw(surface)