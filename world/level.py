import math
import pygame
import core.settings as settings
from core.api import API
from core.utils import get_tile, tile_to_pixel, make_middle_tile
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
        
    def _add_carpet(self, carpet: pygame.Rect, type: str = "carpet"):
        textures = self.textures[type]

        for x in range(carpet.left, carpet.right):
            if x == carpet.left:
                horiz = "left"
            elif x == carpet.right - 1:
                horiz = "right"
            else:
                horiz = "middle"
            
            for y in range(carpet.top, carpet.bottom):
                if y == carpet.top:
                    vert = "top"
                elif y == carpet.bottom - 1:
                    vert = "bottom"
                else:
                    vert = "middle"
                
                carpet_tile = Tile(
                    pos=(tile_to_pixel(x), tile_to_pixel(y)),
                    surface=textures[f"{vert}-{horiz}"],
                    layer=settings.LAYERS["floor"]
                )
                self.tiles.add(carpet_tile)
                
    def _add_tile(self, tile, is_tile: bool = True, is_obstacle: bool = True, is_npc: bool = False, is_door: bool = False, is_ticking: bool = False, is_interactable: bool = False):
        if is_tile: self.tiles.add(tile)
        if is_obstacle: self.obstacles.add(tile)
        if is_npc: self.npcs.add(tile)
        if is_door: self.doors.add(tile)
        if is_ticking: self.ticking_tiles.add(tile)
        if is_interactable: self.interactables.append(tile)
        
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
    def __init__(self, rect: pygame.Rect, project_data: dict, textures: dict, api: object, wall_locations: dict, spawn_point: tuple, has_exit: bool = None):
        super().__init__(rect=rect, textures=textures, wall_locations=wall_locations, spawn_point=spawn_point, has_exit=has_exit)
        self.data = project_data
        self.api = api
        self.super_star = project_data.get("is_super_star", False)
        
        self.generate_altar()
        self.generate_npc()
        
        # Add details based on the amount of hours
        if self.data["stats"]["total_hours"] >= 10.0: self.generate_tier_one()
        if self.data["stats"]["total_hours"] >= 25.0: self.generate_tier_two()
        if self.data["stats"]["total_hours"] >= 50.0: self.generate_tier_three()
        if self.data["stats"]["total_hours"] >= 100.0: self.generate_tier_four()
        
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
            layer=settings.LAYERS["decoration"]
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
        
        if self.super_star:
            top_flag_y = pixel_y - tile_to_pixel(1) + 4
            bottom_flag_y = top_flag_y + tile_to_pixel(1)
            x = pixel_x

            flag_bottom = Tile(
                pos=(x, bottom_flag_y),
                surface=self.textures["flag"]["bottom"],
            )
            flag_top = Tile(
                pos=(x, top_flag_y),
                surface=self.textures["flag"]["top"],
            )
            
            flag_top.depth = bottom_altar.rect.bottom + 0.1
            flag_bottom.depth = bottom_altar.rect.bottom + 0.2
            self._add_tile(flag_bottom, is_obstacle=False)
            self._add_tile(flag_top, is_obstacle=False)
    
    def generate_npc(self):
        # Parse stats
        stats = self.data["stats"]
        
        project_hours = stats.get("total_hours", 0)
        days = round(project_hours / 24, 1)
        universe_percent = (days / 5_035_598_347_500) * 100
        
        total_projects = self.api.get_total_count(count_type="projects")
        rank_hours = stats.get("rank_hours") or total_projects
        beaten_percent_in_hours = (abs(total_projects - rank_hours) / total_projects) * 100
        
        project_stardust = stats.get("stardust_total", 0)
        rank_stardust = stats.get("rank_stardust") or total_projects
        
        # Spawn the NPC
        test_npc = NPC(
            name="Starling",
            dialogue=[
                f"Hey there {self.data["owner_username"]}! I've searched around the darkest corners of the universe to gather as much information about {self.data["title"]} as possible.",
                f"Did you know you've spent {project_hours} hours on this project? That's {days} entire days of pure dedication. Sure, that's only {universe_percent:.13f}% of the universe's lifespan, but it shines just as bright as any star in the cosmos!",
                f"In fact, you've put more time into this than {beaten_percent_in_hours:.2f}% of the {total_projects} projects out there on Stardance, earning rank #{rank_hours} on the leaderboards!",
                f"As for the galactic treasure, you've gathered {project_stardust} stardust from forging this project! That puts you at rank #{rank_stardust} out of all {total_projects} projects on the leaderboards."
            ],
            textures={
              "active": pygame.image.load("assets/characters/looking_star.png" if not self.super_star else "assets/characters/looking_purple_star.png"),
              "inactive": pygame.image.load("assets/characters/standing_star.png" if not self.super_star else "assets/characters/standing_purple_star.png")
            },
            character_path="assets/characters/bean.png" if not self.super_star else "assets/characters/buku.png",
            project_data=self.data,
            obstacles=self.obstacles,
            pos=(self.rect.centerx - 3, self.rect.centery)
        )
        self.npcs.add(test_npc)
        self.interactables.append(test_npc.trigger)
        
    def generate_tier_one(self):
        # Add bed
        bed_x = tile_to_pixel(self.rect.right - 1) - 7
        bottom_bed_y = tile_to_pixel(self.rect.bottom - 1) - 2
        top_bed_y = bottom_bed_y + tile_to_pixel(-1)
        bed_bottom = Tile(
            pos=(bed_x, bottom_bed_y),
            surface=self.textures["bed"]["bottom"],
        )
        bed_top = Tile(
            pos=(bed_x, top_bed_y),
            surface=self.textures["bed"]["top"],
            hitbox=pygame.Rect(bed_x, top_bed_y + 6, 16, 10),
        )
        self._add_tile(bed_bottom)
        self._add_tile(bed_top)
        
        # Add bookcase above the bed
        bookcase_x = tile_to_pixel(self.rect.right - 1) - 5
        bottom_bookcase_y = tile_to_pixel(self.rect.bottom - 3) - 2
        top_bookcase_y = tile_to_pixel(self.rect.bottom - 4) - 2
        bookcase_top = Tile(
            pos=(bookcase_x, top_bookcase_y),
            surface=self.textures["side-bookcase"]["top"],
            hitbox=pygame.Rect(bookcase_x + 4, top_bookcase_y + 8, 12, 8)
        )
        bookcase_bottom = Tile(
            pos=(bookcase_x, bottom_bookcase_y),
            surface=self.textures["side-bookcase"]["bottom"],
            hitbox=pygame.Rect(bookcase_x + 4, bottom_bookcase_y, 12, 15)
        )
        self._add_tile(bookcase_top)
        self._add_tile(bookcase_bottom)
        
    def generate_tier_two(self):
        # Add a carpet beneath the altar
        carpet = pygame.Rect(
            self.rect.centerx - 1, 
            self.rect.centery - 1,
            3,
            3
        )
        self._add_carpet(carpet=carpet, type="small_carpet")
        
        # Add a statue
        for statue_x in (tile_to_pixel(self.rect.centerx + 1), tile_to_pixel(self.rect.centerx - 1)):
            bottom_statue_y = tile_to_pixel(self.rect.centery - 2) - 3
            top_statue_y = bottom_statue_y - 16
            statue_bottom = Tile(
                pos=(statue_x, bottom_statue_y),
                surface=self.textures["statue"]["bottom"],
                hitbox=pygame.Rect(statue_x + 2, bottom_statue_y + 1, 12, 15)
            )
            statue_top = Tile(
                pos=(statue_x, top_statue_y),
                surface=self.textures["statue"]["top"],
                hitbox=pygame.Rect(statue_x + 2, top_statue_y, 12, 0),
                layer=settings.LAYERS["front_decoration"]
            )
            self._add_tile(statue_bottom)
            self._add_tile(statue_top)
            
    def generate_tier_three(self):
        # Add a table with an axe on it
        left_x = tile_to_pixel(self.rect.left + 2)
        right_x = tile_to_pixel(self.rect.left + 3)
        top_y = tile_to_pixel(self.rect.bottom - 4)
        bottom_y = tile_to_pixel(self.rect.bottom - 3)
        
        for x, horiz in ((left_x, "left"), (right_x, "right")):            
            for y, vert in ((top_y, "top"), (bottom_y, "bottom")):
                hitbox_width = 16 if horiz == "left" else 15
                hitbox_height = 12 if vert == "bottom" else 6
                hitbox_top = y if vert == "bottom" else y + 10
                
                table_tile = Tile(
                    pos=(x, y),
                    surface=self.textures["table"][f"{horiz}-{vert}"],
                    hitbox=pygame.Rect(x, hitbox_top, hitbox_width, hitbox_height),
                    layer=settings.LAYERS["back_wall"]
                )
                self._add_tile(table_tile)
                
        # Add an axe on the table
        axe = Tile(
            pos=(left_x + 8, top_y + 8),
            surface=self.textures["axe"],
            layer=settings.LAYERS["decoration"],
            hitbox=pygame.Rect(left_x + 8, top_y + 12, 16, 12)
        )
        self._add_tile(axe)
        
        # Add a bottle next to the table
        bottle = Tile(
            pos=(tile_to_pixel(self.rect.left) + 3, top_y),
            surface=self.textures["rounded_bottle"],
            hitbox=pygame.Rect(tile_to_pixel(self.rect.left) + 7, top_y + 3, 9, 13)
        )
        self._add_tile(bottle)
        
    def generate_tier_four(self):
        # Add a better carpet
        carpet = pygame.Rect(
            self.rect.centerx - 1, 
            self.rect.centery - 1,
            3,
            3
        )
        self._add_carpet(carpet=carpet, type="large_carpet")
        
        # Add a bar
        bar = pygame.Rect(self.rect.centerx - 2, self.rect.top + 1, 5, 3)
        for x in range(bar.left, bar.right):
            for y in range(bar.top, bar.bottom):
                if bar.left < x < bar.right - 1 and y < bar.bottom - 1:
                    continue
                
                if x == bar.left:
                    horiz = "left"
                elif x == bar.right - 1:
                    horiz = "right"
                else:
                    horiz = "middle"
                    
                if y == bar.top:
                    vert = "top"
                elif y == bar.bottom - 1:
                    vert = "bottom"
                else:
                    vert = "side"


                hitbox_width = 16 if horiz == "middle" else 10
                hitbox_left = tile_to_pixel(x) + 6 if horiz == "left" else tile_to_pixel(x)

                if vert == "top":
                    hitbox_height = 4
                    hitbox_top = tile_to_pixel(y) + 12
                elif vert == "bottom":
                    hitbox_height = 12
                    hitbox_top = tile_to_pixel(y) + 3
                else:
                    hitbox_height = 16
                    hitbox_top = tile_to_pixel(y)

                bar_tile = Tile(
                    pos=(tile_to_pixel(x), tile_to_pixel(y)),
                    surface=self.textures["bar"][f"{vert}-{horiz}"],
                    hitbox=pygame.Rect(hitbox_left, hitbox_top, hitbox_width, hitbox_height)
                )
                self._add_tile(bar_tile)
                
            # Add a sword on the bar
            left_sword_x = tile_to_pixel(self.rect.centerx)
            right_sword_x = left_sword_x + tile_to_pixel(1)
            sword_y = tile_to_pixel(bar.bottom - 1) - 5
            
            left_sword = Tile(
                pos=(left_sword_x, sword_y),
                surface=self.textures["sword"]["left"],
                layer=settings.LAYERS["decoration"]
            )
            right_sword = Tile(
                pos=(right_sword_x, sword_y),
                surface=self.textures["sword"]["right"],
                layer=settings.LAYERS["decoration"]
            )
            
            right_sword.depth = tile_to_pixel(bar.bottom) + 0.1
            left_sword.depth = tile_to_pixel(bar.bottom) + 0.1
            self._add_tile(left_sword, is_obstacle=False)
            self._add_tile(right_sword, is_obstacle=False)
            
            # Add candles
            candle_y = tile_to_pixel(bar.bottom - 2)
            for x in (tile_to_pixel(bar.left) + 2, tile_to_pixel(bar.right - 1) - 3):
                candle = Tile(
                    pos=(x, candle_y),
                    surface=self.textures["candle"]
                )
                self._add_tile(candle, is_obstacle=False)
                
            # Add some flower pots next to the entrance
            bottom_flowerpot_y = tile_to_pixel(self.rect.bottom - 1) + 5
            top_flowerpot_y = bottom_flowerpot_y - tile_to_pixel(1)
            for x in (tile_to_pixel(self.rect.centerx - 1), tile_to_pixel(self.rect.centerx + 1)):
                flowerpot_bottom = Tile(
                    pos=(x, bottom_flowerpot_y),
                    surface=self.textures["flower_pot"]["bottom"],
                    hitbox=pygame.Rect(x + 2, bottom_flowerpot_y + 3, 12, 13)
                )
                flowerpot_top = Tile(
                    pos=(x, top_flowerpot_y),
                    surface=self.textures["flower_pot"]["top"]
                )
                self._add_tile(flowerpot_bottom)
                flowerpot_top.depth = flowerpot_bottom.rect.bottom
                self._add_tile(flowerpot_top, is_obstacle=False)
            
                                        
class Hallway(Room):
    def __init__(self, textures: dict, api: object, height):
        self.textures = textures
        self.projects = api.get_projects()
        self.api = api
        
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
            
            hours = project["stats"]["total_hours"]
            project_room_width = int(9 + 2.4 * hours ** 0.3) // 2 * 2 + 1
            project_room_height = int(7 + 2.4 * hours ** 0.3) // 2 * 2 + 1
            
            project_room = ProjectRoom(
                rect=pygame.Rect(0, 0, project_room_width, project_room_height),
                project_data=project,
                textures=self.textures,
                api=self.api,
                wall_locations={
                    "left": True,
                    "right": True,
                    "top": True,
                    "bottom": True
                },
                spawn_point=(project_room_width // 2, project_room_height - 1, "up"),
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

        self._add_carpet(carpet=carpet)

class Level:
    def __init__(self, display_surface, ui_manager):
        self.display_surface = display_surface
        self.ui_manager = ui_manager
        self.api = API()
        self.obstacles = pygame.sprite.Group()
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
                "top-middle": get_tile(tile_x=4, tile_y=0, tilesheet=self.tilesheet),
                "top-right": get_tile(tile_x=5, tile_y=0, tilesheet=self.tilesheet),
                "middle-left": make_middle_tile(get_tile(tile_x=3, tile_y=0, tilesheet=self.tilesheet), get_tile(tile_x=3, tile_y=1, tilesheet=self.tilesheet)),
                "middle-middle": make_middle_tile(get_tile(tile_x=4, tile_y=0, tilesheet=self.tilesheet), get_tile(tile_x=4, tile_y=1, tilesheet=self.tilesheet)),
                "middle-right": make_middle_tile(get_tile(tile_x=5, tile_y=0, tilesheet=self.tilesheet), get_tile(tile_x=5, tile_y=1, tilesheet=self.tilesheet)),
                "bottom-left": get_tile(tile_x=3, tile_y=1, tilesheet=self.tilesheet),
                "bottom-middle": get_tile(tile_x=4, tile_y=1, tilesheet=self.tilesheet),
                "bottom-right": get_tile(tile_x=5, tile_y=1, tilesheet=self.tilesheet),
            },
            "small_carpet": {
                "top-left": get_tile(tile_x=0, tile_y=0, tilesheet=self.tilesheet),
                "top-middle": get_tile(tile_x=1, tile_y=0, tilesheet=self.tilesheet),
                "top-right": get_tile(tile_x=2, tile_y=0, tilesheet=self.tilesheet),
                "middle-left": make_middle_tile(get_tile(tile_x=0, tile_y=0, tilesheet=self.tilesheet), get_tile(tile_x=0, tile_y=1, tilesheet=self.tilesheet)),
                "middle-middle": make_middle_tile(get_tile(tile_x=1, tile_y=0, tilesheet=self.tilesheet), get_tile(tile_x=1, tile_y=1, tilesheet=self.tilesheet)),
                "middle-right": make_middle_tile(get_tile(tile_x=2, tile_y=0, tilesheet=self.tilesheet), get_tile(tile_x=2, tile_y=1, tilesheet=self.tilesheet)),
                "bottom-left": get_tile(tile_x=0, tile_y=1, tilesheet=self.tilesheet),
                "bottom-middle": get_tile(tile_x=1, tile_y=1, tilesheet=self.tilesheet),
                "bottom-right": get_tile(tile_x=2, tile_y=1, tilesheet=self.tilesheet),
            },
            "large_carpet": {
                "top-left": get_tile(tile_x=7, tile_y=6, tilesheet=self.expanded_tilesheet),
                "top-middle": get_tile(tile_x=8, tile_y=6, tilesheet=self.expanded_tilesheet),
                "top-right": get_tile(tile_x=10, tile_y=6, tilesheet=self.expanded_tilesheet),
                "middle-left": get_tile(tile_x=7, tile_y=7, tilesheet=self.expanded_tilesheet),
                "middle-middle": get_tile(tile_x=8, tile_y=7, tilesheet=self.expanded_tilesheet),
                "middle-right": get_tile(tile_x=10, tile_y=7, tilesheet=self.expanded_tilesheet),
                "bottom-left": get_tile(tile_x=7, tile_y=9, tilesheet=self.expanded_tilesheet),
                "bottom-middle": get_tile(tile_x=8, tile_y=9, tilesheet=self.expanded_tilesheet),
                "bottom-right": get_tile(tile_x=10, tile_y=9, tilesheet=self.expanded_tilesheet),
            },
            "altar": {
                "top": get_tile(tile_x=4, tile_y=6, tilesheet=self.expanded_tilesheet),
                "bottom": get_tile(tile_x=4, tile_y=8, tilesheet=self.expanded_tilesheet)
            },
            "book": {
                "open": get_tile(tile_x=3, tile_y=8, tilesheet=self.expanded_tilesheet),
                "upside": get_tile(tile_x=1, tile_y=8, tilesheet=self.expanded_tilesheet),
                "closed": get_tile(tile_x=3, tile_y=11, tilesheet=self.expanded_tilesheet)
            },
            "bed": {
                "top": get_tile(tile_x=4, tile_y=4, tilesheet=self.tilesheet),
                "bottom": get_tile(tile_x=4, tile_y=5, tilesheet=self.tilesheet)
            },
            "statue": {
                "top": get_tile(tile_x=3, tile_y=4, tilesheet=self.tilesheet),
                "bottom": get_tile(tile_x=3, tile_y=5, tilesheet=self.tilesheet)
            },
            "axe": get_tile(tile_x=0, tile_y=7, tilesheet=self.tilesheet),
            "bookcase": {
                "top-left": get_tile(tile_x=3, tile_y=6, tilesheet=self.tilesheet),
                "bottom-left": get_tile(tile_x=3, tile_y=7, tilesheet=self.tilesheet),
                "top-right": get_tile(tile_x=4, tile_y=6, tilesheet=self.tilesheet),
                "bottom-right": get_tile(tile_x=4, tile_y=7, tilesheet=self.tilesheet),
            },
            "side-bookcase": {
                "top": get_tile(tile_x=6, tile_y=10, tilesheet=self.tilesheet),
                "bottom": get_tile(tile_x=6, tile_y=11, tilesheet=self.tilesheet)
            },
            "sword": {
                "left": get_tile(tile_x=1, tile_y=7, tilesheet=self.tilesheet),
                "right": get_tile(tile_x=2, tile_y=7, tilesheet=self.tilesheet),
            },
            "table": {
                "left-top": get_tile(tile_x=5, tile_y=7, tilesheet=self.tilesheet),
                "left-bottom": get_tile(tile_x=5, tile_y=8, tilesheet=self.tilesheet),
                "right-top": get_tile(tile_x=6, tile_y=7, tilesheet=self.tilesheet),
                "right-bottom": get_tile(tile_x=6, tile_y=8, tilesheet=self.tilesheet)
            },
            "bar": {
                "top-left": get_tile(tile_x=0, tile_y=8, tilesheet=self.tilesheet),
                "top-right": get_tile(tile_x=4, tile_y=8, tilesheet=self.tilesheet),
                "side-left": get_tile(tile_x=0, tile_y=9, tilesheet=self.tilesheet),
                "side-right": get_tile(tile_x=4, tile_y=9, tilesheet=self.tilesheet),
                "bottom-left": get_tile(tile_x=0, tile_y=11, tilesheet=self.tilesheet),
                "bottom-middle": get_tile(tile_x=2, tile_y=11, tilesheet=self.tilesheet),
                "bottom-right": get_tile(tile_x=4, tile_y=11, tilesheet=self.tilesheet),
            },
            "candle": get_tile(tile_x=2, tile_y=11, tilesheet=self.expanded_tilesheet),
            "rounded_bottle": get_tile(tile_x=2, tile_y=8, tilesheet=self.expanded_tilesheet),
            "flower_pot": {
                "top": get_tile(tile_x=8, tile_y=10, tilesheet=self.expanded_tilesheet),
                "bottom": get_tile(tile_x=8, tile_y=11, tilesheet=self.expanded_tilesheet),
            },
            "flag": {
                "top": get_tile(tile_x=9, tile_y=2, tilesheet=self.expanded_tilesheet),
                "bottom": get_tile(tile_x=9, tile_y=3, tilesheet=self.expanded_tilesheet),
            },
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