import math
import csv
import geopy.distance as geodistance
import locale
INDEX = 0
G=0.0000003
from queue import SimpleQueue, Queue
from functools import lru_cache

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
        self.connections = set()
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
        city1.connections.remove(con)
        city2.connections.remove(con)
    else:
        s = Segment(city1, city2)
        city1.connections.add(s)
        city2.connections.add(s)


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
        return f"{self.start.name} to {self.end.name}, {round(self.distance, 1):n} miles"

    def get_width(self, scale=1):
        return max(int(math.sqrt(self.utilization * scale)), 1)


class Route:
    def __init__(self, start: City, end: City, segments : list[Segment]) -> None:
        self.start = start
        self.end = end
        self.segments = segments

    def __str__(self):
        return f"{self.start.name} to {self.end.name}, cost {round(self.get_cost()):n} hours"

    @lru_cache()
    def get_cost(self):
        return sum([i.cost for i in self.segments])

    @lru_cache()
    def get_utilization(self):
        return (G * self.start.population * self.end.population) / self.get_cost() ** 2

def route_exists(routes: list[Route], city1: City, city2: City) -> Route | bool:
    for route in routes:
        if route.start == city1 and route.end == city2:
            return route
        elif route.start == city2 and route.end == city1:
            return route
    return False


def build_routes(city: City):
    global ROUTES
    cities = SimpleQueue()
    seen_cities = set()
    cities.put((city, []))

    while not cities.empty():
        workingcity, workingpath = cities.get()
        seen_cities.add(workingcity)
        #print(f"Processing {workingcity.name} via")
        #for segment in workingpath:
        #    print(f" - {segment}")

        for segment in workingcity.connections:
            if segment.start == workingcity:
                target = segment.end
            elif segment.end == workingcity:
                target = segment.start
            else: assert False
            if target not in seen_cities:
                cities.put((target, workingpath + [segment]))

        if city != workingcity:
            rte = Route(city, workingcity, workingpath)
            #print(rte)

            if existing := route_exists(ROUTES, city, workingcity):
                if rte.get_cost() < existing.get_cost():
                    #print(f"Replacing {existing} with {rte}")
                    ROUTES.remove(existing)
                    ROUTES.append(rte)
                else:
                    #print(f"Not replacing {existing} with {rte}")
                    pass
            else:
                ROUTES.append(rte)

def print_route(route: Route):
    print(f"Starting at {route.start.name}, Ending at {route.end.name}, costing {route.get_cost():n}")
    for segment in route.segments:
        print(f" - {segment}")
    print(f"")

def print_routes(routes: list[Route] = None):
    if routes is None:
        global ROUTES
        routes = ROUTES[:]
    routes.sort(key=lambda route: route.get_cost())
    for route in routes:
        print_route(route)

def build_all_routes():
    global ROUTES
    ROUTES = []
    for city in CITIES:
        build_routes(city)

def build_traffic_values():
    global SEGMENTS, ROUTES
    for segment in SEGMENTS:
        segment.utilization = 0

    for route in ROUTES:
        for segment in route.segments:
            segment.utilization += route.get_utilization()

    for segment in SEGMENTS:
        print(f"Traffic rating of {segment.start.name} to {segment.end.name}: {segment.utilization}")