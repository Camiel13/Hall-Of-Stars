import pygame
import settings
from utils import get_tile, tile_to_pixel

# TODO: ADD CAMERA LOGIC
class Room:
    def __init__(self, rect: pygame.Rect, textures: dict, wall_locations: dict):
        self.rect = rect
        self.textures = textures
        
        self.wall_locations = wall_locations
        self.tiles = []
        self.obstacles = pygame.sprite.Group()
        
        # Generate the room
        self.generate_floor()
        self.generate_side_walls()
        self.generate_front_walls()
        
    def generate_floor(self):
        for x in range(self.rect.left, self.rect.right):
            for y in range(self.rect.top, self.rect.bottom):
                pixel_x, pixel_y = tile_to_pixel(x), tile_to_pixel(y)
                
                floor_tile = Tile(pos=(pixel_x, pixel_y), surface=self.textures["floor"], layer=settings.LAYERS["floor"])
                self.tiles.append(floor_tile)
                
    def generate_side_walls(self):
        pixel_left_x = tile_to_pixel(self.rect.left)
        pixel_right_x = tile_to_pixel(self.rect.right - 1)
        
        right_image = self.textures["side_wall"]
        left_image = pygame.transform.flip(right_image, True, False)
        
        for y in range(self.rect.top, self.rect.bottom):
            pixel_y = tile_to_pixel(y)
            
            if self.wall_locations.get("left", True):
                left_tile = Tile((pixel_left_x, pixel_y), pygame.transform.flip(self.textures["side_wall"], True, False), layer=settings.LAYERS["side_wall"])
                self.tiles.append(left_tile)
            if self.wall_locations.get("right", True):
                right_tile = Tile((pixel_right_x, pixel_y), self.textures["side_wall"], layer=settings.LAYERS["side_wall"])
                self.tiles.append(right_tile)
            
    def generate_front_walls(self):
        pixel_y_top = tile_to_pixel(self.rect.top)
        pixel_y_bottom = tile_to_pixel(self.rect.bottom)
        
        for x in range(self.rect.left, self.rect.right):
            pixel_x = tile_to_pixel(x)
            
            if self.wall_locations.get("top", True):
                top_tile = Tile((pixel_x, pixel_y_top), self.textures["front_wall"], layer=settings.LAYERS["back_wall"])
                self.tiles.append(top_tile)
            if self.wall_locations.get("bottom", True):
                bottom_tile = Tile((pixel_x, pixel_y_bottom), self.textures["front_wall"], layer=settings.LAYERS["front_wall"])  
                self.tiles.append(bottom_tile)

class Hallway(Room):
    def __init__(self, textures: dict, api: object, height):
        self.textures = textures
        self.projects = api.get_projects()
        
        self.door_spacing = settings.DOOR_SPACING
        self.door_margin = settings.DOOR_MARGIN
        self.hallway_width = self.calculate_width()
        self.hallway_height = height
        
        self.rect = pygame.Rect(0, 0, self.hallway_width, self.hallway_height)
        super().__init__(
            rect=self.rect,
            textures=self.textures,
            wall_locations={
                "left": True,
                "right": True,
                "top": True,
                "bottom": True
            }
        )
        self.generate_doors()
        
    def calculate_width(self):
        doors = len(self.projects)
        
        return doors + ((doors - 1) * self.door_spacing) + (2 * self.door_margin) if doors > 0 else 5
    
    def generate_doors(self):
        doors = len(self.projects)
        
        for door_index in range(doors):
            x_tile = self.door_margin + (door_index * (1 + self.door_spacing))
            pixel_x = tile_to_pixel(x_tile)
            
            door_tile = Door(pos=(pixel_x, 0), surface=self.textures["door"], project_data={}, layer=settings.LAYERS["door"])
            self.tiles.append(door_tile)

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surface, layer=settings.LAYERS["decoration"]):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self._layer = layer

class Door(Tile):
    def __init__(self, pos, surface, project_data, layer=settings.LAYERS["door"]):
        super().__init__(pos=pos, surface=surface, layer=layer)
        self.project_data = project_data
        
    def interact(self):
        pass # TODO: ADD DOOR OPENING LOGIC
        
class Level:
    def __init__(self, camera, api):
        self.api = api
        self.camera_group = camera
        
        self.tilesheet = pygame.image.load("assets/level/tileset.png").convert_alpha()

        # Get all the textures        
        self.textures = {
            "floor": get_tile(tile_x=6, tile_y=0, tilesheet=self.tilesheet),
            "side_wall": get_tile(tile_x=2, tile_y=5, tilesheet=self.tilesheet),
            "front_wall": get_tile(tile_x=0, tile_y=6, tilesheet=self.tilesheet),
            "door": get_tile(tile_x=1, tile_y=5, tilesheet=self.tilesheet)
        }

        # Set the heights and generate the hallway
        self.main_hallway = Hallway(
            textures=self.textures,
            api=self.api,
            height=6
        )
        self.camera_group.add(self.main_hallway.tiles)