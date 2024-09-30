import math
import csv
import geopy.distance as geodistance
import locale

locale.setlocale(locale.LC_ALL, '')


class City:
    def __init__(self, location, population, color, name):
        self.lat, self.lon = location
        self.population = population
        self.color = color
        self.name = name
        self.connections = []

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

def connect_cities(city1 : City, city2 : City) -> None:
    if city1 in city2.connections:
        city1.connections.remove(city2)
        city2.connections.remove(city1)
    else:
        city1.connections.append(city2)
        city2.connections.append(city1)

def load_cities(filename='msa.csv', color=None) -> list[City]:
    data = csv.reader(open(filename, encoding='utf-8'))
    cities = []
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
        cities.append(city)
        #print(city)
    return cities

def write_cities(cities : list[City], filename='edited.csv') -> None:
    file = open(filename, 'w', encoding='utf-8', newline='')
    writer = csv.writer(file)
    for city in cities:
        if city.population > 0:
            writer.writerow([city.name, city.population, city.lat, city.lon])
    file.close()