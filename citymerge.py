from city import *
from matplotlib import pyplot as plt
import csv
import openpyxl
from geopy.geocoders import Nominatim
import time
from tqdm import tqdm, trange
geolocator = Nominatim(user_agent="Sophie's Inter City Rail Game")

if __name__ == "__main__":
    cities = load_cities("google_cbsa.csv")

    for i, city1 in enumerate(cities):
        for city2 in cities[i+1:]:
            dist = city1.get_distance(city2)

            if dist < 1:
                print(f"{city1.name} pop {city1.population}, {city2.name} pop {city2.population}")
                if city1.population > city2.population:
                    city1.population += city2.population
                    city2.population = 0

    print("------")

    for i, city1 in enumerate(cities):
        for city2 in cities[i+1:]:
            dist = city1.get_distance(city2)

            if dist < 1:
                #print(f"{city1.name} pop {city1.population}, {city2.name} pop {city2.population}")
                if city1.population > city2.population:
                    city1.population += city2.population
                    city2.population += 0


    write_cities(cities, "google_edited.csv")
