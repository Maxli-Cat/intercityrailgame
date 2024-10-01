import math
import csv
import geopy.distance as geodistance
import locale
INDEX = 0
G=0.0000003

locale.setlocale(locale.LC_ALL, '')

CITIES = []
SEGMENTS = []
ROUTES = []


class City:
    def __init__(self, location, population, color, name):
        global INDEX, CITIES
        self.index = INDEX
        INDEX += 1
        self.lat, self.lon = location
        self.population = population
        self.color = color
        self.name = name
        self.routes = []
        CITIES.append(self)

    def __str__(self):
        return f"{self.name}, ({self.lat}, {self.lon}), {self.population:n}"

    def get_location(self) -> (float, float):
        return self.lat, self.lon

    def get_color(self) -> (int, int, int):
        return self.color

    def get_size(self, scale=1.0, min=1.0) -> (float):
        zoomdir = {
            1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0,
            7: 1.5, 8: 2.0, 9: 2.5, 10: 3.0, 11: 3.5, 12: 4.0,
            13: 4.5, 14: 5.0, 15: 5.0, 16: 5.5, 17: 6.0, 18: 6.0, 19: 6.0
        }
        min = zoomdir[min]
        return max(min, ((self.population)**(1/3) / 15)) * scale

    def get_distance(self, other) -> float:
        return geodistance.geodesic(self.get_location(), other.get_location()).miles

def get_connection(city1: City, city2: City):
    for segment in SEGMENTS:
        if segment.start == city1 and segment.end == city2:
            return segment
        elif segment.start == city2 and segment.end == city1:
            return segment
    return False

def connect_cities(city1 : City, city2 : City) -> None:
    if con := get_connection(city1, city2):
        SEGMENTS.remove(con)
    else:
        Segment(city1, city2)



def save_connections(cities : list[City], filename : str = "connections.save"):
    file = open(filename, "w", newline='')
    writer = csv.writer(file)
    for segment in SEGMENTS:
        city = segment.start
        connection = segment.end
        writer.writerow([city.name, connection.name])

def load_connections(cities : list[City], filename : str = "connections.save"):
    data = csv.reader(open(filename))
    for row in data:
        try:
            first_city = [i for i in cities if i.name == row[0]][0]
        except IndexError:
            print(f"Cannot find {row[0]}")
            continue
        try:
            second_city = [i for i in cities if i.name == row[1]][0]
        except IndexError:
            print(f"Cannot find {row[1]}")
            continue
        connect_cities(first_city, second_city)

def load_cities(filename='msa.csv', color=None) -> None:
    data = csv.reader(open(filename, encoding='utf-8'))
    for row in data:
        name = row[0]
        population = int(row[1])
        if population > 1000000:
            color = (255,0,0)
        elif population > 100000:
            color = (255, 127, 0)
        elif population > 10000:
            color = (127, 0, 255)
        else:
            color = (0,0,255)
        lat = float(row[2])
        lon = float(row[3])
        city = City(location=(lat, lon), population=population, color=color, name=name)
        #print(city)
    #return cities

def write_cities(cities : list[City], filename='edited.csv') -> None:
    file = open(filename, 'w', encoding='utf-8', newline='')
    writer = csv.writer(file)
    for city in cities:
        if city.population > 0:
            writer.writerow([city.name, city.population, city.lat, city.lon])
    file.close()

class Segment:
    def __init__(self, start : City, end : City, speed = 1, capacity = float('inf')) -> None:
        global SEGMENTS
        self.start = start
        self.end = end
        self.distance = geodistance.geodesic(start.get_location(), end.get_location()).miles
        self.cost = self.distance / speed
        self.capacity = capacity
        self.utilization = 1
        SEGMENTS.append(self)

    def __str__(self) -> str:
        return f"{self.start.name} to {self.end.name}, {self.distance:n} miles"


class Route:
    def __init__(self, start: City, end: City, points : list[City]) -> None:
        self.start = start
        self.end = end
