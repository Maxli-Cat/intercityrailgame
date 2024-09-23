import math
import csv

class City:
    def __init__(self, location, population, color, name):
        self.lat, self.lon = location
        self.population = population
        self.color = color
        self.name = name

    def __str__(self):
        return f"{self.name}, ({self.lat}, {self.lon}), {self.get_size()}"

    def get_location(self) -> (float, float):
        return self.lat, self.lon

    def get_color(self) -> (int, int, int):
        return self.color

    def get_size(self, scale=1) -> (float):
        return max(3.0, ((self.population)**(1/3) / 15)) * scale


def load_cities(filename='msa.csv') -> list[City]:
    data = csv.reader(open(filename, encoding='utf-8'))
    cities = []
    for row in data:
        name = row[0]
        population = int(row[1])
        if population > 900000:
            color = (255,0,0)
        elif population > 200000:
            color = (255, 127, 0)
        else:
            color = (0,0,255)
        lat = float(row[2])
        lon = float(row[3])
        city = City(location=(lat, lon), population=population, color=color, name=name)
        cities.append(city)
        #print(city)
    return cities