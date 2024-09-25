import api_keys
from city import *
from matplotlib import pyplot as plt
import csv
import openpyxl
from geopy.geocoders import Nominatim, GoogleV3
import time
from tqdm import tqdm, trange
import api_keys
from city import *

geolocator = Nominatim(user_agent="Sophie's Inter City Rail Game")
gogle = GoogleV3(api_key=api_keys.google, user_agent="Intercity Rail Game")

if __name__ == "__main__":
#    amfile = csv.reader(open("amtrak\\stations.csv", encoding="utf-8"))
#    amfile = [i for i in amfile if len(i[0]) > 1]
#    #print(*amfile, sep="\n")
#    stops = []
#    seen = set()
#    for line in amfile:
#        name = line[0]
#        lookup_name = f"{line[2]}, {line[3]}"
#        if lookup_name in seen: continue
#        print(lookup_name)
#        #time.sleep(0.1)
#        location = gogle.geocode(lookup_name)
#        stops.append((name, 1, location.latitude, location.longitude))
#        seen.add(lookup_name)
#
#    csv.writer(open("amtrak_raw.csv", "w", encoding='utf-8', newline='')).writerows(stops)

    amstations = load_cities("distant_amtrak.csv")
    for station in (amstations):
        location = station.get_location()
        reverse = geolocator.reverse(location, exactly_one=True, zoom=10)
        station.name = str(reverse)
        population = input(f"{station.name} population ")
        population = int(population)
        station.population = population

    write_cities(amstations, "populated_amtrak.csv")


