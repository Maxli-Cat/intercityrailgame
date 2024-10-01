import pygame
import sys
import time
import basemap
from functools import lru_cache
import csv
from city import *
import locale
locale.setlocale(locale.LC_ALL, '')
NATIONALISM = False

pygame.init()
pygame.font.init()

font = pygame.font.SysFont("Arial", 18)
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

def draw_cities(cities : list[City], start, screen, zoom, scale=1, highlighted : City = None):

    scale = max(1.0, (zoom - 6) / 3) * scale
    for city in cities:
        if zoom < 9:
            draw_dot(position=city.get_location(), screen=screen, startcorner=start, zoom=zoom, radius=city.get_size(scale=scale, min=zoom )+1, color=(255,255,255))
        draw_dot(position=city.get_location(), screen=screen, startcorner=start, zoom=zoom, radius=city.get_size(scale=scale, min=zoom ), color=city.get_color())
        #draw_dot(position=city.get_location(), screen=screen, startcorner=start, zoom=zoom, radius=10, color=city.get_color())
        if zoom > 8:
            name = font.render(f"{city.name.split(',')[0]},   #{city.index}", True, (5,5,5))
            name_size = name.get_size()
            namex, namey = basemap.real_coords_to_map_coords_fixed(*city.get_location(), startcorner=startcorner, zoom=zoom)
            namey += city.get_size(scale=scale, min=zoom )
            namex -= name_size[0]//2
            pygame.draw.rect(screen, (250, 250, 250), ((namex, namey), name_size))
            screen.blit(name, (namex, namey))
        if zoom > 9:
            pop = font.render(f"Population: {city.population:n}", True, (10,10,10))
            pop_size = pop.get_size()
            popx, popy = basemap.real_coords_to_map_coords_fixed(*city.get_location(), startcorner=startcorner, zoom=zoom)
            popy += city.get_size(scale=scale, min=zoom ) + name_size[1]
            popx -= pop_size[0]//2
            pygame.draw.rect(screen, (250, 250, 250), ((popx, popy), pop_size))
            screen.blit(pop, (popx, popy))
    if highlighted is not None:
        draw_dot(position=highlighted.get_location(), screen=screen, startcorner=start, zoom=zoom, radius=10, color=(255,255,0))

def draw_links( start, screen, zoom, scale=1):
    for segment in SEGMENTS:
        city = segment.start
        link = segment.end
        start = basemap.real_coords_to_map_coords_fixed(*city.get_location(), startcorner=startcorner, zoom=zoom)
        end = basemap.real_coords_to_map_coords_fixed(*link.get_location(), startcorner=startcorner, zoom=zoom)
        pygame.draw.line(screen, (0, 0, 0), start, end, width=segment.get_width(scale=scale))

def screen_draw(screen, startcorner, zoom, cities = (), highlighted = None):
    draw_tiles(startcorner, pygame.display.get_surface().get_size(), screen, zoom=zoom)
    #draw_msa(start=startcorner, screen=screen, zoom=zoom, filename="msa.csv")
    draw_links(start=startcorner, zoom=zoom, screen=screen)
    draw_cities(cities=cities, start=startcorner, zoom=zoom, screen=screen, highlighted=highlighted)
    draw_attribution(screen)

def checkbounds(startcorner):
    if startcorner[0] > 75:
        startcorner = (75, startcorner[1])
    return startcorner

def buildcityposlist(cities : list[City], startcorner : [float, float], zoom : int, screensize : tuple[int, int]):
    positions = []
    for city in cities:
        pos = basemap.real_coords_to_map_coords_fixed(city.lat, city.lon, startcorner=startcorner, zoom=zoom)
        if 0 < pos[0] < screensize[0] and 0 < pos[1] < screensize[1]:
            positions.append((pos, city))
    return positions

def check_city_clicked(cities : list[((float, float), City)], click: (float, float), zoom : int):

    for target, city in cities:
        margin = max(10, city.get_size(min=zoom))
        if target[0] - margin < click[0] < target[0] + margin and target[1] - margin < click[1] < target[1] + margin:
            return city
    return False


if __name__ == "__main__":
    lastmouse = (0,0)
    dragged = False
    offsetfactors = (1,1)
    lastclicked = None

    load_cities("USA_bordered.csv")
    if NATIONALISM:
        load_cities("US_ONLY_North.csv")
        load_cities("US_ONLY_South.csv")
    else:
        load_cities("US_CAN_BORDER.csv")
        load_cities("US_MEX_Border.csv")

    city_positions = buildcityposlist(CITIES, startcorner, zoom_factor, screen.get_size())
    try:
        load_connections(CITIES)
    except FileNotFoundError:
        pass
    #print(*[i[1] for i in city_positions], sep='\n')

    CITIES.sort(key=lambda x:x.population, reverse=False)
    clicked = False
    pygame.display.set_caption("Intercity Rail Game")
    screen.fill((255, 255, 255))
    screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)
    pygame.display.flip()

    while True:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_connections(CITIES)
                print(f"{cache_hits=}, {cache_misses=}, {100 * (cache_hits/(cache_hits+cache_misses))}%")
                basemap.print_cache_stats(cache_misses)
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE or event.type == pygame.VIDEOEXPOSE:
                screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)

            elif event.type == pygame.MOUSEWHEEL:
                screen.fill((255, 255, 255))
                if zoom_factor > 5:
                    if event.y > 0:
                        startcorner = zoom_down(startcorner, pygame.display.get_surface().get_size(), zoom=zoom_factor)
                    else:
                        startcorner = zoom_up(startcorner, pygame.display.get_surface().get_size(), zoom=zoom_factor)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)

                if zoom_factor > 19:
                    zoom_factor = 19

                if event.y > 0 or zoom_factor > 5:
                    zoom_factor += event.y
                    move_factor = 40 / (2 ** zoom_factor)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    startcorner = (startcorner[0] + move_factor, startcorner[1])
                    startcorner = checkbounds(startcorner)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)

                elif event.key == pygame.K_DOWN:
                    startcorner = (startcorner[0] - move_factor, startcorner[1])
                    startcorner = checkbounds(startcorner)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)

                elif event.key == pygame.K_LEFT:
                    startcorner = (startcorner[0], startcorner[1] - move_factor)
                    startcorner = checkbounds(startcorner)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)

                elif event.key == pygame.K_RIGHT:
                    startcorner = (startcorner[0], startcorner[1] + move_factor)
                    startcorner = checkbounds(startcorner)
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)
                elif event.key == pygame.K_RETURN:
                    build_all_routes()
                    build_traffic_values()
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)

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
                    if not dragged:
                        city_positions = buildcityposlist(CITIES, startcorner, zoom_factor, screen.get_size())
                        if city := check_city_clicked(city_positions, pygame.mouse.get_pos(), zoom=zoom_factor):
                            if lastclicked is None:
                                lastclicked = city
                            elif lastclicked is not city:
                                connect_cities(city, lastclicked)
                                lastclicked = None
                            else:
                                lastclicked = None
                        else:
                            lastclicked = None
                    dragged = False
                    screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)

                elif event.button == 3:
                    city_positions = buildcityposlist(CITIES, startcorner, zoom_factor, screen.get_size())
                    if city := check_city_clicked(city_positions, pygame.mouse.get_pos(), zoom=zoom_factor):
                        build_routes(city)

            if clicked:
                newpos = pygame.mouse.get_pos()
                deltay = (newpos[0] - lastmouse[0]) * offsetfactors[0]
                deltax = (newpos[1] - lastmouse[1]) * offsetfactors[1]
                if newpos != lastmouse:
                    dragged = True
                #print(deltax, deltay)
                lastmouse = newpos
                startcorner = (startcorner[0] - deltax, startcorner[1] - deltay)
                startcorner = checkbounds(startcorner)
                screen_draw(screen, startcorner, zoom=zoom_factor, cities=CITIES, highlighted=lastclicked)