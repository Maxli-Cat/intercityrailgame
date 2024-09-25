import api_keys
from city import *
from matplotlib import pyplot as plt
import csv
import openpyxl
from geopy.geocoders import Nominatim, GoogleV3
import time
from tqdm import tqdm, trange
import api_keys

geolocator = Nominatim(user_agent="Sophie's Inter City Rail Game")
gogle = GoogleV3(api_key=api_keys.google, user_agent="Intercity Rail Game")


if __name__ == '__main__':
    places = []

    #cbsas = []
    #cbsa_file_1 = csv.reader(open('census\\cbsa-met-est2023-pop.csv', encoding='utf-8'))
    #cbsa_file_1 = list(cbsa_file_1)[6:-15]
    #cbsa_file_2 = csv.reader(open('census\\cbsa-mic-est2023-pop.csv', encoding='utf-8'))
    #cbsa_file_2 = list(cbsa_file_2)[6:-13]
    #cbsa_files = cbsa_file_1 + cbsa_file_2
#
    #for line in tqdm(cbsa_files):
    #    name = line[0].replace('.','')
    #    if "Division" in name:
    #        continue
    #    #if "County" in name:
    #    #    continue
    #    population = line[5].replace(',','')
    #    population = int(population)
    #    #print(name, population)
#
    #    city, state = name.replace(" Metro Area", "").replace(" Micro Area",'').split(',')
    #    city = city.split("-")[0].strip()
    #    state = state.split("-")[0].strip()
    #    lookup_name = f"{city}, {state}"
    #    if lookup_name == "Winston, NC": lookup_name = "Winston-Salem, NC"
    #    if lookup_name == "Amherst Town, MA": lookup_name = "Amherst, MA"
    #    if lookup_name == "Urban Honolulu, HI": lookup_name = "Honolulu, HI"
    #    try:
    #        time.sleep(.1)
    #        location = geolocator.geocode(lookup_name)
    #        places.append((name, population, location.latitude, location.longitude))
    #    except:
    #        print(f"Could not locate {lookup_name} aka {name}")
    #        exit()

    incorp_places = []
    inc_file = csv.reader(open('census\\SUB-IP-EST2023-POP.csv', encoding='utf-8'))
    inc_file = list(inc_file)[4:-6]
    #print(*inc_file[:5], sep='\n')
    #print(*inc_file[-5:], sep='\n')

    for line in tqdm(inc_file):
        name = ((line[0].replace(" city", "").replace(" town", "")
                .replace(" village", "").replace(" Village of Islands,", ""))
                .replace(", Moore County metropolitan government", ""))
        if len(name) < 1: continue
        population = line[5].replace(",","")
        population = int(population)
        if population < 2500: continue
        try:
            city, state = name.split(',')
        except ValueError:
            print(name)
            exit()
        city = city.split("-")[0].strip()
        state = state.split("-")[0].strip()
        lookup_name = f"{city}, {state}"
        #print(lookup_name)
        try:
            time.sleep(.1)
            location = gogle.geocode(lookup_name)
            places.append((name, population, location.latitude, location.longitude))
        except:
            print(f"Could not locate {lookup_name} aka {name}")



    csv.writer(open("google_incorp.csv", "w", encoding='utf-8', newline='')).writerows(places)
