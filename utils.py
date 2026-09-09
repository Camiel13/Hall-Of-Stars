import pygame
import settings

def get_image(sheet, frame_index, frame_width=settings.CHARACTER_SIZE, frame_height=settings.CHARACTER_SIZE):
    x = frame_index * frame_width
    y = 0
    return sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))

def get_animation(sheet, start_frame, count=4):
    frames = []
    for i in range(count):
        frames.append(get_image(sheet=sheet, frame_index=start_frame+i))
        
    return frames

def flip_animation(frames):
    return [pygame.transform.flip(frame, True, False) for frame in frames]

def get_tile(tile_x, tile_y, tilesheet, tile_width=settings.TILE_SIZE, tile_height=settings.TILE_SIZE):
    tx, ty = tile_width, tile_height
    return tilesheet.subsurface(pygame.Rect(tile_x * tx, tile_y * ty, tx, ty))

def tile_to_pixel(tile):
    return tile * settings.TILE_SIZE