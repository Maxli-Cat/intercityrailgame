import pygame
import sys
import time
import basemap
from functools import lru_cache

pygame.init()
pygame.font.init()

font = pygame.font.SysFont("Arial", 30)
small = pygame.font.SysFont("Courier New", 15)
FLAGS = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE
SIZE = WIDTH, LENGTH = (900, 600)

screen = pygame.display.set_mode(SIZE, FLAGS)

startcorner = [43.0133468,-71.4952949]

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


def calc_offset_factors(lat, lon, zoom, aspect=1.0):
    tile = basemap.get_tile_cords(lat=lat, lon=lon, zoom=zoom)
    topleft = basemap.get_tile_corner(zoom, *tile)
    bottomright = basemap.get_tile_corner(zoom, tile[0]+1, tile[1]+1)
    deltax = topleft[0] - bottomright[0]
    deltay = topleft[1] - bottomright[1]
    return ((deltax / 256) * aspect, (deltay / 256) * 1/aspect)

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

def draw_dot(position, screen, startcorner, color=(255,255,255), zoom=14, radius=5):
    screnpos = basemap.real_coords_to_map_coords_fixed(*position, startcorner=startcorner, zoom=zoom)
    pygame.draw.circle(screen, color, screnpos, radius)


def middle(a, b):
    return (a + b) / 2

def cord_middle(a, b):
    return (middle(a[0], b[0]), middle(a[1], b[1]))

def zoom_down(corner, size, zoom):
    top_corner_tile = basemap.get_tile_cords(zoom, *corner)
    xcount = (size[0] // 256) + 2
    ycount = (size[1] // 256) + 2
    bottom_corner_tile = (top_corner_tile[0] + xcount, top_corner_tile[1] + ycount)
    top_corner = basemap.get_tile_corner(zoom, *top_corner_tile)
    bottom_corner = basemap.get_tile_corner(zoom, *bottom_corner_tile)
    center = cord_middle(top_corner, bottom_corner)
    new_corner = cord_middle(top_corner, center)
    return list(new_corner)

def zoom_up(corner, size, zoom):
    top_corner_tile = basemap.get_tile_cords(zoom, *corner)
    xcount = (size[0] // 256)
    ycount = (size[1] // 256)
    bottom_corner_tile = (top_corner_tile[0] + xcount, top_corner_tile[1] + ycount)
    top_corner = basemap.get_tile_corner(zoom, *top_corner_tile)
    bottom_corner = basemap.get_tile_corner(zoom, *bottom_corner_tile)
    xoffset = (top_corner[0] - bottom_corner[0]) / 2
    yoffset = (top_corner[1] - bottom_corner[1]) / 2

    new_top_corner = [top_corner[0] + xoffset, top_corner[1] + yoffset]
    return new_top_corner

@lru_cache()
def load_msas(filenames):
    file = open(filenames).read().split('\n')
    dataset = [i.split(', ') for i in file if len(i) > 1]
    points = [(float(i[2]), float(i[3])) for i in dataset]
    return points

def draw_msa(start, screen, zoom, filename="msa_usa.csv"):
    points = load_msas(filename)
    for point in points:
        draw_dot(position=point, screen=screen, startcorner=start, zoom=zoom, radius=5, color=(255,0,0))


def screen_draw(screen, startcorner, zoom):
    draw_tiles(startcorner, pygame.display.get_surface().get_size(), screen, zoom=zoom)
    draw_msa(start=startcorner, screen=screen, zoom=zoom)

if __name__ == "__main__":
    lastmouse = (0,0)
    offsetfactors = (1,1)
    clicked = False
    pygame.display.set_caption("Intercity Rail Game")
    screen.fill((255, 255, 255))
    screen_draw(screen, startcorner, zoom=zoom_factor)
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
                screen_draw(screen, startcorner, zoom=zoom_factor)

            elif event.type == pygame.MOUSEWHEEL:
                screen.fill((255, 255, 255))
                if event.y > 0:
                    startcorner = zoom_down(startcorner, pygame.display.get_surface().get_size(), zoom=zoom_factor)
                else:
                    startcorner = zoom_up(startcorner, pygame.display.get_surface().get_size(), zoom=zoom_factor)

                zoom_factor += event.y
                move_factor = 40 / (2 ** zoom_factor)
                screen_draw(screen, startcorner, zoom=zoom_factor)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    startcorner = (startcorner[0] + move_factor, startcorner[1])
                    screen_draw(screen, startcorner, zoom=zoom_factor)

                elif event.key == pygame.K_DOWN:
                    startcorner = (startcorner[0] + move_factor, startcorner[1])
                    screen_draw(screen, startcorner, zoom=zoom_factor)

                elif event.key == pygame.K_LEFT:
                    startcorner = (startcorner[0], startcorner[1] - move_factor)
                    screen_draw(screen, startcorner, zoom=zoom_factor)

                elif event.key == pygame.K_RIGHT:
                    startcorner = (startcorner[0], startcorner[1] + move_factor)
                    screen_draw(screen, startcorner, zoom=zoom_factor)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
                    lastmouse = pygame.mouse.get_pos()
                    size = pygame.display.get_surface().get_size()
                    aspect = size[0] / size[1]
                    offsetfactors = calc_offset_factors(*startcorner, zoom=zoom_factor, aspect=aspect)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    clicked = False

            if clicked:
                newpos = pygame.mouse.get_pos()
                deltay = (newpos[0] - lastmouse[0]) * offsetfactors[0]
                deltax = (newpos[1] - lastmouse[1]) * offsetfactors[1]
                #print(deltax, deltay)
                lastmouse = newpos
                startcorner = (startcorner[0] - deltax, startcorner[1] - deltay)
                screen_draw(screen, startcorner, zoom=zoom_factor)