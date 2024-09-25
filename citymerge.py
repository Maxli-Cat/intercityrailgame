from city import *
from matplotlib import pyplot as plt
import csv
import openpyxl
from geopy.geocoders import Nominatim
import time
from tqdm import tqdm, trange
geolocator = Nominatim(user_agent="Sophie's Inter City Rail Game")

if __name__ == "__main__":
    existing = load_cities("merged_and_filtered2.csv")[:]
    #cbsas = load_cities("google_edited.csv")

#    for i, city1 in enumerate(tqdm(incorps)):
#        for city2 in incorps[i+1:]:
#            dist = city1.get_distance(city2)
#
#            if dist < 10:
#                print(f"{city1.name} pop {city1.population}, {city2.name} pop {city2.population}")
#                if city1.population > city2.population:
#                    city1.population += city2.population
#                    city2.population = 0
#                else:
#                    city2.population += city1.population
#                    city1.population = 0
#
#
#    deleted = [i for i in incorps if i.population == 0]
#    print(*deleted, sep="\n")
#    write_cities(incorps, "merged_and_filtered2.csv")

    #for cbsa in tqdm(cbsas):
    #    for incorp in incorps:
    #        dist = cbsa.get_distance(incorp)
    #        if dist < 25:
    #            incorp.population = 0
#
    #cities = cbsas + incorps
    #print(f"CBSAs: {len(cbsas)}")
    #print(f"Incorperated Areas: {len([i for i in incorps if i.population > 0])}")
    #write_cities(cities, "merged_wider.csv")

    amstops = load_cities("distant_amtrak.csv")
    distant_stops = []
    distances = []
    rememvbered = "nnynnynyyynynnnyyyynyynyyynynynnyyynynynynnnynynnnyyynyyynnnyyynyynnnnyyyyyyynynynnynnnyyyyyyynnnnyyyyynnnyyynnnyyynyynynnyynyyyy"

    for i, stop in enumerate(amstops):
        bestcity = ""
        bestdist = float('inf')
        for city in (existing):
            dist = stop.get_distance(city)
            if dist < bestdist:
                bestcity = city
                bestdist = dist

        print(f"{stop.name} (population: {stop.population}) is {round(bestdist, 2)} from {bestcity.name} (population: {bestcity.population})")
        print(f"https://www.openstreetmap.org/#map=13/{stop.lat}/{stop.lon}")
        try:
            answer = rememvbered[i]
        except IndexError:
            answer = input("Merge?")
        if answer not in "yesYes":
            distances.append(bestdist)
            distant_stops.append(stop)
        #if bestdist > 10:
        #    distant_stops.append(stop)
    plt.hist(distances)
    plt.show()

    write_cities(distant_stops, "filtered_amtrak_again.csv")