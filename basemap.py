import xyzservices.providers as xyz
import math
import urllib.request
import os
import time
from tqdm import tqdm, trange

style = "Mapnik"

def sec(x):
    return 1/math.cos(x)

def arsinh(x):
    return math.log(x + (x**2 + 1)**0.5)

def get_tile_cords(zoom, lat, lon):
    n = 2 ** zoom
    xtile = n * ((lon + 180) / 360)
    lat = math.radians(lat)
    ytile = n * (1 - (math.log(math.tan(lat) + sec(lat)) / math.pi)) /2
    return (int(xtile), int(ytile))

def get_tile_corner(zoom, x, y):
    n = 2 ** zoom
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def download_tile(z, x, y, basepath="tiles"):
    #url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    #style = "Mapnik"
    #url = f"https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
    url = xyz['OpenStreetMap'][style]['url']
    url = url.replace('{s}','a').replace('{z}', f'{z}').replace('{x}', f'{x}').replace('{y}', f'{y}')
    #print(url)
    #exit()
    #print(url)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Sophie Johnson Intercity Rail Game 0.0.1')]
    urllib.request.install_opener(opener)
    print(url)
    urllib.request.urlretrieve(url, f"{basepath}\\{style}_{z}_{x}_{y}.png")
    time.sleep(0.1)

downloaded = 0

def get_tile(z, x, y, basepath="tiles"):
    if x < 0 or y < 0 or z < 1: return
    global downloaded
    filename = f"{basepath}\\{style}_{z}_{x}_{y}.png"
    if not os.path.exists(filename):
        download_tile(z, x, y, basepath)
        downloaded += 1
        return
    filetime = os.path.getmtime(filename)
    age = time.time() - filetime
    if age > (60 * 60 * 24 * 30):
        download_tile(z, x, y, basepath)

def print_cache_stats(undownloaded):
    print(f"{undownloaded=}, {downloaded=}, {(undownloaded/(downloaded + undownloaded))*100}%")

def get_tiles(startlat, startlon, endlat, endlon, zoom, basepath="tiles"):
    starttile = get_tile_cords(zoom, startlat, startlon)
    endtile = get_tile_cords(zoom, endlat, endlon)
    print(starttile, endtile)

    for x in trange(starttile[0], endtile[0]+1):
        for y in range(starttile[1], endtile[1]+1):
            #print(x, y)
            get_tile(zoom, x, y, basepath)

    return (starttile[0], endtile[0]+1), (starttile[1], endtile[1]+1)

def get_count_tiles(start, xcount, ycount, zoom, basepath="tiles"):
    starttile = get_tile_cords(zoom, *start)

    for x in range(starttile[0], starttile[0]+xcount):
        for y in range(starttile[1], starttile[1]+ycount):
            get_tile(zoom, x, y, basepath)

    return (starttile[0], starttile[0] + xcount), (starttile[1], starttile[1] + ycount)

def point_in_range(point, start, end):
    point = point - start
    end = end - start
    return point / end

def get_offset(zoom, lat, lon):
    on = get_tile_cords(zoom, lat, lon)
    off = [i+1 for i in on]
    topleft = get_tile_corner(zoom, *on)
    bottomright = get_tile_corner(zoom, *off)
    #print(topleft, (lat,lon), bottomright)
    x = point_in_range(lat, topleft[0], bottomright[0])
    y = point_in_range(lon, topleft[1], bottomright[1])
    return (x * 255, y * 255)

def real_coords_to_map_coords_fixed(lat, lon, startcorner, zoom):
    corner_tile = get_tile_cords(zoom, *startcorner)
    targer_tile = get_tile_cords(zoom, lat, lon)
    delta_x = (corner_tile[0] - targer_tile[0]) * -256
    delta_y = (corner_tile[1] - targer_tile[1]) * -256
    corner_offset = get_offset(zoom, *startcorner)
    target_offset = get_offset(zoom, lat, lon)
    delta_x += (256 - corner_offset[1])
    delta_y += (256 - corner_offset[0])

    delta_x -= (256 - target_offset[1])
    delta_y -= (256 - target_offset[0])

    return delta_x, delta_y


if __name__ == '__main__':
    for zoom in range(0, 19):
        coords = get_tile_cords(zoom, 43.052976, -71.073759)
        #print(f"https://tile.openstreetmap.org/{zoom}/{coords[0]}/{coords[1]}.png")
        #corner = get_tile_corner(zoom, *coords)
        #print(*corner)
        #get_tile(zoom, coords[0], coords[1])

    startcorner = (43.0733739,-71.1216099)
    endcorner = (43.0050499,-71.0245459)

    get_tiles(startcorner[0], startcorner[1], endcorner[0], endcorner[1], 14)
    #coords = get_tile_cords(16, 43.044308, -71.077123)
    #get_tile(16, coords[0], coords[1])
    #get_offset(16, 43.044308, -71.077123)