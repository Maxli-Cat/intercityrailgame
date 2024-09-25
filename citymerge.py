from city import *
from matplotlib import pyplot as plt
import csv
import openpyxl
from geopy.geocoders import Nominatim
import time
from tqdm import tqdm, trange
geolocator = Nominatim(user_agent="Sophie's Inter City Rail Game")

if __name__ == "__main__":
    incorps = load_cities("incorp_edited_wider.csv")
    cbsas = load_cities("google_edited.csv")

    #for i, city1 in enumerate(tqdm(incorps)):
    #    for city2 in incorps[i+1:]:
    #        dist = city1.get_distance(city2)
#
    #        if dist < 10:
    #            #print(f"{city1.name} pop {city1.population}, {city2.name} pop {city2.population}")
    #            if city1.population > city2.population:
    #                city1.population += city2.population
    #                city2.population = 0
#
    #write_cities(incorps, "incorp_edited_wider.csv")

    for cbsa in tqdm(cbsas):
        for incorp in incorps:
            dist = cbsa.get_distance(incorp)
            if dist < 25:
                incorp.population = 0

    cities = cbsas + incorps
    print(f"CBSAs: {len(cbsas)}")
    print(f"Incorperated Areas: {len([i for i in incorps if i.population > 0])}")
    write_cities(cities, "merged_wider.csv")
