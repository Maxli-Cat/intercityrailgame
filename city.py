import math

class City:
    def __init__(self, location, population, color, name):
        self.lat, self.lon = location
        self.population = population
        self.color = color
        self.name = name

    def __str__(self):
        return f"{self.name}, ({self.lat}, {self.lon}), {self.get_size()}"

    def get_location(self):
        return self.lat, self.lon

    def get_color(self):
        return self.color

    def get_size(self, scale=1):
        return max(3.0, ((self.population)**(1/3) / 15)) * scale
