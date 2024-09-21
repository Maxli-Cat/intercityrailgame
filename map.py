import pygame
import sys
import time
import basemap

pygame.init()
pygame.font.init()

font = pygame.font.SysFont("Arial", 30)
small = pygame.font.SysFont("Courier New", 15)
FLAGS = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE
SIZE = WIDTH, LENGTH = (900, 600)

screen = pygame.display.set_mode(SIZE, FLAGS)

startcorner = [***REMOVED***]

zoom_factor = 13
move_factor = 40 / (2 ** zoom_factor)

tile_surfaces = {}
cache_hits = 0
cache_misses = 0

def get_images_cache(zoom, x, y):
    global cache_hits, cache_misses
    key = f"{zoom}_{x}_{y}"
    if key in tile_surfaces.keys():
        cache_hits += 1
        return tile_surfaces[key]
    cache_misses += 1
    filename = f"tiles\\{basemap.style}_{zoom}_{x}_{y}.png"
    image = pygame.image.load(filename).convert()
    tile_surfaces[key] = image
    return image

def draw_tiles(start, size, screen, zoom=14):
    xcount = (size[0] // 256) + 2
    ycount = (size[1] // 256) + 2
    tile_range = basemap.get_count_tiles(start, xcount, ycount, zoom)

    startoffset = basemap.get_offset(zoom, *start)
    startoffset = (0-startoffset[1], 0-startoffset[0])
    #startoffset = (0,0)
    #start_coords = basemap.get_tile_cords(13, *start)
    for i, xtile in enumerate(range(*tile_range[0])):
        for j, ytile in enumerate(range(*tile_range[1])):

            image = get_images_cache(zoom, xtile, ytile)
            offset = (startoffset[0] + (i * 256), startoffset[1] + (j * 256))
            screen.blit(image, offset)

if __name__ == "__main__":
    pygame.display.set_caption("Intercity Rail Game")
    screen.fill((255, 255, 255))
    draw_tiles(startcorner, pygame.display.get_surface().get_size(), screen, zoom=zoom_factor)
    pygame.display.flip()

    while True:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(f"{cache_hits=}, {cache_misses=}, {100 * (cache_hits/(cache_hits+cache_misses))}%")
                basemap.print_cache_stats(cache_misses)
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE or event.type == pygame.VIDEOEXPOSE:
                draw_tiles(startcorner, pygame.display.get_surface().get_size(), screen, zoom=zoom_factor)

            elif event.type == pygame.MOUSEWHEEL:
                screen.fill((255, 255, 255))
                zoom_factor += event.y
                move_factor = 40 / (2 ** zoom_factor)
                draw_tiles(startcorner, pygame.display.get_surface().get_size(), screen, zoom=zoom_factor)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    startcorner[0] += move_factor
                    draw_tiles(startcorner, pygame.display.get_surface().get_size(), screen, zoom=zoom_factor)

                elif event.key == pygame.K_DOWN:
                    startcorner[0] -= move_factor
                    draw_tiles(startcorner, pygame.display.get_surface().get_size(), screen, zoom=zoom_factor)

                elif event.key == pygame.K_LEFT:
                    startcorner[1] -= move_factor
                    draw_tiles(startcorner, pygame.display.get_surface().get_size(), screen, zoom=zoom_factor)

                elif event.key == pygame.K_RIGHT:
                    startcorner[1] += move_factor
                    draw_tiles(startcorner, pygame.display.get_surface().get_size(), screen, zoom=zoom_factor)
