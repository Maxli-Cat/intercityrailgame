import pygame
import sys
import time
import basemap
from functools import lru_cache
import csv
from city import City, load_cities

pygame.init()
pygame.font.init()

font = pygame.font.SysFont("Arial", 30)
small = pygame.font.SysFont("Courier New", 15)
FLAGS = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE
SIZE = WIDTH, LENGTH = (900, 600)

screen = pygame.display.set_mode(SIZE, FLAGS)

startcorner = [43.0133468,-71.4952949]

zoom_factor = 10
move_factor = 40 / (2 ** zoom_factor)

tile_surfaces = {}
cache_hits = 0
cache_misses = 0

def get_images_cache(zoom, x, y):
    global cache_hits, cache_misses
    if zoom < 1: zoom = 1
    if x < 0 or y < 0:
        x = 0
        y = 0
        zoom = 0
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

def draw_attribution(screen, string="(C) OpenStreetMap contributors"):
    string = f"Zoom: {zoom_factor}\t" + string
    text = small.render(string, True, (5,5,5))
    text_size = text.get_size()
    screen_size = screen.get_size()
    top_corner = (screen_size[0] - text_size[0], screen_size[1] - text_size[1])
    pygame.draw.rect(screen, (250,250,250), (top_corner, text_size))
    screen.blit(text, top_corner)

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
    file = open(filenames, encoding='utf-8').read().split('\n')
    dataset = [i.split(',') for i in file if len(i) > 1]
    #points = [(float(i[2]), float(i[3])) for i in dataset]
    points = []
    for line in dataset:
        try:
            point = float(line[2]), float(line[3])
            points.append(point)
        except IndexError:
            print(line)
            exit()
    return points

def draw_msa(start, screen, zoom, filename="msa_usa.csv"):
    points = load_msas(filename)
    for point in points:
        draw_dot(position=point, screen=screen, startcorner=start, zoom=zoom, radius=5, color=(255,0,0))



def draw_cities(cities : list[City], start, screen, zoom, scale=1):
    zoomdir = {
        1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0,
        7: 1.5, 8: 2.0, 9: 2.5, 10: 3.0, 11: 3.5, 12: 4.0,
        13: 4.5, 14: 5.0, 15: 5.0, 16: 5.5, 17: 6.0, 18:6.0, 19: 6.0
    }
    for city in cities:
        draw_dot(position=city.get_location(), screen=screen, startcorner=start, zoom=zoom, radius=city.get_size(scale=scale, min=zoomdir[zoom]), color=city.get_color())


def screen_draw(screen, startcorner, zoom, cities = ()):
    draw_tiles(startcorner, pygame.display.get_surface().get_size(), screen, zoom=zoom)
    #draw_msa(start=startcorner, screen=screen, zoom=zoom, filename="msa.csv")
    draw_cities(cities=cities, start=startcorner, zoom=zoom, screen=screen)
    draw_attribution(screen)

def checkbounds(startcorner):
    if startcorner[0] > 75:
        startcorner = (75, startcorner[1])
    return startcorner

if __name__ == "__main__":
    lastmouse = (0,0)
    offsetfactors = (1,1)
    cities = load_cities("merged_wider.csv")
    clicked = False
    pygame.display.set_caption("Intercity Rail Game")
    screen.fill((255, 255, 255))
    screen_draw(screen, startcorner, zoom=zoom_factor, cities=cities)
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
                screen_draw(screen, startcorner, zoom=zoom_factor, cities=cities)

            elif event.type == pygame.MOUSEWHEEL:
                screen.fill((255, 255, 255))
                if zoom_factor > 5:
                    if event.y > 0:
                        startcorner = zoom_down(startcorner, pygame.display.get_surface().get_size(), zoom=zoom_factor)
                    else:
                        startcorner = zoom_up(startcorner, pygame.display.get_surface().get_size(), zoom=zoom_factor)

                if event.y > 0 or zoom_factor > 5:
                    zoom_factor += event.y
                    move_factor = 40 / (2 ** zoom_factor)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=cities)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    startcorner = (startcorner[0] + move_factor, startcorner[1])
                    startcorner = checkbounds(startcorner)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=cities)

                elif event.key == pygame.K_DOWN:
                    startcorner = (startcorner[0] - move_factor, startcorner[1])
                    startcorner = checkbounds(startcorner)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=cities)

                elif event.key == pygame.K_LEFT:
                    startcorner = (startcorner[0], startcorner[1] - move_factor)
                    startcorner = checkbounds(startcorner)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=cities)

                elif event.key == pygame.K_RIGHT:
                    startcorner = (startcorner[0], startcorner[1] + move_factor)
                    startcorner = checkbounds(startcorner)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=cities)

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
                startcorner = checkbounds(startcorner)
                screen_draw(screen, startcorner, zoom=zoom_factor, cities=cities)