# Screen and resolution
INTERNAL_WIDTH = 256
INTERNAL_HEIGHT = 192

SCALE = 4
WINDOW_WIDTH = INTERNAL_WIDTH * SCALE
WINDOW_HEIGHT = INTERNAL_HEIGHT * SCALE

FPS = 60

# Raster
TILE_SIZE = 16
CHARACTER_SIZE = 24
DOOR_SPACING = 4
DOOR_MARGIN = 3

# Colors
COLORS = {
    "background": (48, 48, 48)
}

# Layers
LAYERS = {
    "floor": 0,
    "back_wall": 1,
    "side_wall": 2,
    "door": 3,
    "decoration": 4,
    "player": 5,
    "front_wall": 6
}