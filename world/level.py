import math
import pygame
import core.settings as settings
from core.api import API
from core.utils import get_tile, tile_to_pixel
from entities.player import Player
from entities.npc import NPC
from world.camera import CameraGroup
from world.tiles import Tile, Door, FloatingTile, InteractionTrigger
from ui import KeybindOverlay, create_project_sequence

class Room:
    def __init__(self, rect: pygame.Rect, textures: dict, wall_locations: dict, spawn_point: tuple, has_exit: bool = None, project_data: dict = {}):
        self.rect = rect
        self.textures = textures
        
        self.wall_locations = wall_locations
        self.spawn_point = spawn_point
        
        # Groups
        self.tiles = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.ticking_tiles = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.interactables = []
        
        # Generate the room
        self.generate_floor()
        self.generate_side_walls()
        self.generate_front_walls()
        if has_exit:
            self.generate_exit_door()
        
    def generate_floor(self):
        for x in range(self.rect.left, self.rect.right):
            for y in range(self.rect.top, self.rect.bottom):
                pixel_x, pixel_y = tile_to_pixel(x), tile_to_pixel(y)
                
                floor_tile = Tile(pos=(pixel_x, pixel_y), surface=self.textures["floor"], layer=settings.LAYERS["floor"])
                self.tiles.add(floor_tile)
                
    def generate_side_walls(self):
        pixel_left_x = tile_to_pixel(self.rect.left)
        pixel_right_x = tile_to_pixel(self.rect.right - 1)
        
        right_image = self.textures["side_wall"]
        left_image = pygame.transform.flip(right_image, True, False)
        
        for y in range(self.rect.top, self.rect.bottom + 1):
            pixel_y = tile_to_pixel(y)
            
            if self.wall_locations.get("left", True):
                left_tile = Tile(
                    pos=(pixel_left_x, pixel_y),
                    surface=pygame.transform.flip(self.textures["side_wall"], True, False),
                    hitbox=pygame.Rect(pixel_left_x, pixel_y, 5, 16),
                    layer=settings.LAYERS["side_wall"]
                )
                self.tiles.add(left_tile)
                self.obstacles.add(left_tile)
            if self.wall_locations.get("right", True):
                right_tile = Tile(
                    pos=(pixel_right_x, pixel_y),
                    surface=self.textures["side_wall"],
                    hitbox=pygame.Rect(pixel_right_x + 11, pixel_y, 5, 16),
                    layer=settings.LAYERS["side_wall"]
                )
                self.tiles.add(right_tile)
                self.obstacles.add(right_tile)
            
    def generate_front_walls(self):
        pixel_y_top = tile_to_pixel(self.rect.top)
        pixel_y_bottom = tile_to_pixel(self.rect.bottom)
        
        for x in range(self.rect.left, self.rect.right):
            pixel_x = tile_to_pixel(x)
            
            if self.wall_locations.get("top", True):
                top_tile = Tile(
                    pos=(pixel_x, pixel_y_top),
                    surface=self.textures["front_wall"],
                    layer=settings.LAYERS["back_wall"]
                )
                self.tiles.add(top_tile)
                self.obstacles.add(top_tile)
            if self.wall_locations.get("bottom", True):
                bottom_tile = Tile(
                    pos=(pixel_x, pixel_y_bottom),
                    surface=self.textures["front_wall"],
                    hitbox=pygame.Rect(pixel_x, pixel_y_bottom + 10, 16, 6),
                    layer=settings.LAYERS["front_wall"]
                )  
                self.tiles.add(bottom_tile)
                self.obstacles.add(bottom_tile)           
                
    def generate_exit_door(self):
        pixel_x = tile_to_pixel(self.rect.centerx)
        pixel_y = tile_to_pixel(self.rect.bottom)            
                    
        self.exit_door = Door(
            pos=(pixel_x, pixel_y),
            surface=self.textures["door"],
            layer=settings.LAYERS["front_wall"],
            hitbox=pygame.Rect(pixel_x, pixel_y + 9, 16, 7)
        )
        self.tiles.add(self.exit_door)
        self.doors.add(self.exit_door)
        
    def tick_doors(self, player: pygame.Rect) -> object:
        for door in self.doors:
            if (player.direction == "up" or player.direction == "down") and player.hitbox.colliderect(door.hitbox):
                return door
            
        return None
    
    def tick_ticking_tiles(self):
        for tile in self.ticking_tiles:
            tile.tick()
            
    def tick_interactables(self, player):
        for interactable in self.interactables:
            interactable.tick(player=player)
            
    def tick_npcs(self):
        for npc in self.npcs:
            npc.tick()
            
    def tick(self, player: pygame.Rect):
        self.tick_doors(player=player)
        self.tick_interactables(player=player)
        self.tick_ticking_tiles()
        self.tick_npcs()
    
    def load(self, camera: object, obstacles: object):
        camera.add(self.tiles)
        camera.add(self.npcs)
        obstacles.add(self.obstacles)
        obstacles.add(self.npcs)
        
    def unload(self, camera: object, obstacles: object):
        camera.remove(self.tiles)
        camera.remove(self.npcs)
        obstacles.remove(self.obstacles)
        obstacles.remove(self.npcs)

class ProjectRoom(Room):
    def __init__(self, rect: pygame.Rect, project_data: dict, textures: dict, wall_locations: dict, spawn_point: tuple, has_exit: bool = None):
        super().__init__(rect=rect, textures=textures, wall_locations=wall_locations, spawn_point=spawn_point, has_exit=has_exit)
        self.data = project_data
        self.generate_altar()
        
    def generate_altar(self):
        pixel_x = tile_to_pixel(self.rect.centerx)
        pixel_y = tile_to_pixel(self.rect.centery)
        
        # Generate the altar
        bottom_altar = Tile(
            pos=(pixel_x, pixel_y),
            surface=self.textures["altar"]["bottom"],
            layer=settings.LAYERS["decoration"]
        )
        self.tiles.add(bottom_altar)
        self.obstacles.add(bottom_altar)
        
        top_altar = Tile(
            pos=(pixel_x, pixel_y - tile_to_pixel(1)),
            surface=self.textures["altar"]["top"],
            hitbox=pygame.Rect(pixel_x, pixel_y + 10, 16, 6),
            layer=settings.LAYERS["front_decoration"]
        )
        self.tiles.add(top_altar)
        self.obstacles.add(top_altar)
        
        # Generate the floating book
        self.book = FloatingTile(
            pos=(pixel_x, pixel_y - 25),
            surface=self.textures["book"]["closed"],
            layer=settings.LAYERS["floating"],
        )
        self.tiles.add(self.book)
        self.ticking_tiles.add(self.book)
        
        # Add the interaction zone to the book
        altar_trigger = InteractionTrigger(
            target=self.book,
            zone=bottom_altar.rect.inflate(28, 28),
            keybind=pygame.K_e,
            keybind_text="E",
            text="Project Info",
            on_trigger=lambda: create_project_sequence(self.data),
            textures={"active": self.textures["book"]["open"], "inactive": self.textures["book"]["closed"]}
        )
        self.interactables.append(altar_trigger)
        
        test_npc = NPC(
            name="Starling",
            dialogue=["Hey test!", "Whats up?"],
            textures={
              "active": pygame.image.load("assets/characters/looking_star.png"),
              "inactive": pygame.image.load("assets/characters/standing_star.png")
            },
            obstacles=self.obstacles,
            pos=(2, 2)
        )
        self.npcs.add(test_npc)
        self.interactables.append(test_npc.trigger)
                        
class Hallway(Room):
    def __init__(self, textures: dict, api: object, height):
        self.textures = textures
        self.projects = api.get_projects()
        
        self.doors = pygame.sprite.Group()
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
            },
            spawn_point=((self.hallway_width - 1) / 2, 3, "up"),
        )
        self.generate_doors()
        self.generate_carpet()
        
    def calculate_width(self):
        doors = len(self.projects)
        
        return doors + ((doors - 1) * self.door_spacing) + (2 * self.door_margin) if doors > 0 else 5
    
    def generate_doors(self):
        for door_index, project in enumerate(self.projects):
            x_tile = self.door_margin + (door_index * (1 + self.door_spacing))
            pixel_x = tile_to_pixel(x_tile)
            
            project_room = ProjectRoom(
                rect=pygame.Rect(0, 0, 11, 11),
                project_data=project,
                textures=self.textures,
                wall_locations={
                    "left": True,
                    "right": True,
                    "top": True,
                    "bottom": True
                },
                spawn_point=(5, 10, "up"),
                has_exit=True,
            )
            
            hallway_door = Door(
                pos=(pixel_x, 0),
                surface=self.textures["door"],
                target_room=project_room,
                target_pos=project_room.spawn_point,
                layer=settings.LAYERS["door"],
            )
            self.tiles.add(hallway_door)
            self.doors.add(hallway_door)
            
            project_room.exit_door.target_room = self
            project_room.exit_door.target_pos = (x_tile, 0, "down")
            
    def generate_carpet(self):
        carpet = pygame.Rect(
            self.rect.left + 2, # Leave a 2 tile gap on the left
            self.rect.height - 3, # 2 tiles above the middle
            self.rect.width - 4, # Stretch to 2 tiles before the end
            2
        )

        for x in range(carpet.left, carpet.right):
            if x == carpet.left:
                horiz = "left"
            elif x == carpet.right - 1:
                horiz = "right"
            else:
                horiz = "middle"
            
            for y in range(carpet.top, carpet.bottom):
                vert = "top" if y == carpet.top else "bottom"
                
                carpet_tile = Tile(
                    pos=(tile_to_pixel(x), tile_to_pixel(y)),
                    surface=self.textures["carpet"][f"{vert}-{horiz}"],
                    layer=settings.LAYERS["floor"]
                )
                self.tiles.add(carpet_tile)

class Level:
    def __init__(self, display_surface, ui_manager):
        self.display_surface = display_surface
        self.ui_manager = ui_manager
        self.api = API()
        self.obstacles = pygame.sprite.Group()
        self.camera_group = CameraGroup(display_surface=self.display_surface)
        self.player = Player(obstacles=self.obstacles)
        
        # Make the camera and add the player to it
        self.camera_group = CameraGroup(display_surface=self.display_surface)
        self.camera_group.add(self.player)
        
        # Get all the tiles for the rooms
        self.tilesheet = pygame.image.load("assets/level/tileset.png").convert_alpha()
        self.expanded_tilesheet = pygame.image.load("assets/level/tileset_expansion.png").convert_alpha()
        self.textures = {
            "floor": get_tile(tile_x=6, tile_y=0, tilesheet=self.tilesheet),
            "side_wall": get_tile(tile_x=2, tile_y=5, tilesheet=self.tilesheet),
            "front_wall": get_tile(tile_x=0, tile_y=6, tilesheet=self.tilesheet),
            "door": get_tile(tile_x=1, tile_y=5, tilesheet=self.tilesheet),
            "carpet": {
                "top-left": get_tile(tile_x=3, tile_y=0, tilesheet=self.tilesheet),
                "bottom-left": get_tile(tile_x=3, tile_y=1, tilesheet=self.tilesheet),
                "top-middle": get_tile(tile_x=4, tile_y=0, tilesheet=self.tilesheet),
                "bottom-middle": get_tile(tile_x=4, tile_y=1, tilesheet=self.tilesheet),
                "top-right": get_tile(tile_x=5, tile_y=0, tilesheet=self.tilesheet),
                "bottom-right": get_tile(tile_x=5, tile_y=1, tilesheet=self.tilesheet),
            },
            "altar": {
                "top": get_tile(tile_x=4, tile_y=6, tilesheet=self.expanded_tilesheet),
                "bottom": get_tile(tile_x=4, tile_y=8, tilesheet=self.expanded_tilesheet)
            },
            "book": {
                "open": get_tile(tile_x=3, tile_y=8, tilesheet=self.expanded_tilesheet),
                "upside": get_tile(tile_x=1, tile_y=8, tilesheet=self.expanded_tilesheet),
                "closed": get_tile(tile_x=3, tile_y=11, tilesheet=self.expanded_tilesheet)
            }
        }
        
        self.generate_hallway()
        
    def generate_hallway(self):
        # Set the heights and generate the hallway
        self.hallway = Hallway(
            textures=self.textures,
            api=self.api,
            height=5,
        )
        self.current_room = self.hallway
        self.hallway.load(camera=self.camera_group, obstacles=self.obstacles)
        self.player.set_pos((self.current_room.spawn_point))
      
    def switch_room(self, target_room: object):
        self.current_room.unload(camera=self.camera_group, obstacles=self.obstacles)
        self.current_room = target_room
        target_room.load(camera=self.camera_group, obstacles=self.obstacles)
        
    def tick(self):
        self.player.tick()
        self.tick_doors()
        self.current_room.tick(player=self.player)
        self.handle_interactions()    
        
    def tick_doors(self):
        if self.player.direction not in ("up", "down"):
            return

        for door in self.current_room.doors:
            if self.player.hitbox.colliderect(door.hitbox):
                self.switch_room(target_room=door.target_room)
                self.player.set_pos((door.target_pos))
                
    def handle_interactions(self):
        active_interactable = None
        for interactable in self.current_room.interactables:
                if interactable.active:
                    active_interactable = interactable
                    break

        if active_interactable:
            self.ui_manager.set_overlay(
                KeybindOverlay(
                    key=active_interactable.keybind,
                    key_text=active_interactable.keybind_text,
                    text=active_interactable.text,
                    on_trigger=lambda: self.trigger_interaction(active_interactable)
                )
            )
        else:
            self.ui_manager.clear_overlay()
    
    def trigger_interaction(self, interactable):
        if interactable.on_trigger:
            ui = interactable.on_trigger()
            self.ui_manager.set_ui(new_ui=ui)

    
    def draw(self):
        self.camera_group.draw_sprites(target=self.player)