from city import *
from matplotlib import pyplot as plt
import csv
import openpyxl
from geopy.geocoders import Nominatim
import time
from tqdm import tqdm, trange
geolocator = Nominatim(user_agent="Sophie's Inter City Rail Game")

if __name__ == '__main__':
    places = []
    csas = []
    csa_file = csv.reader(open('census\\csa-est2023-pop.csv', encoding='utf-8'))
    csa_file = list(csa_file)[5:-11]

    for line in tqdm(csa_file):
        name = line[0][1:].replace(" CSA", "").replace(".", "")
        population = line[5].replace(',','')
        population = int(population)
        #print(name, population)
        csas.append(name)

        city, state = name.split(',')
        city = city.split("-")[0].strip()
        state = state.split("-")[0].strip()
        lookup_name = f"{city}, {state}"
        if lookup_name == "Winston, NC": lookup_name = "Winston-Salem, NC"
        if lookup_name == "Amherst Town, MA": lookup_name = "Amherst, MA"
        #try:
        #    time.sleep(0.1)
        #    location = geolocator.geocode(lookup_name)
        #except:
        #    print(f"Could not locate {lookup_name} aka {name}")
        #    exit()
        #places.append((name, population, location.latitude, location.longitude))

    #csv.writer(open("csa.csv", "w", encoding='utf-8', newline='')).writerows(places)

    cbsas = []
    cbsa_file_1 = csv.reader(open('census\\cbsa-met-est2023-pop.csv', encoding='utf-8'))
    cbsa_file_1 = list(cbsa_file_1)[6:-15]
    cbsa_file_2 = csv.reader(open('census\\cbsa-mic-est2023-pop.csv', encoding='utf-8'))
    cbsa_file_2 = list(cbsa_file_2)[6:-13]
    cbsa_files = cbsa_file_1 + cbsa_file_2

    cross_file = csv.reader(open('census\\list1_2023.csv'))
    cross_list = list(cross_file)[3:-3]
    cross_dir = {}

    for line in cross_list:
        cbsa = line[3].replace('.','')
        csa = line[6].replace('.','')
        if "PR" in cbsa or "PR" in csa: continue
        if len(csa) < 1:
            csa = None
        elif csa not in csas:
            print(f"{csa} not found in list of populations")
        cross_dir[cbsa] = csa


    for line in tqdm(cbsa_files):
        name = line[0].replace('.','').replace(" Metro Area", "").replace(" Micro Area",'')
        if "Division" in name:
            continue
        #if "County" in name:
        #    continue
        population = line[5].replace(',','')
        population = int(population)
        #print(name, population)
        cbsas.append(name)

        if cross_dir.get(name) is not None:
            city, state = name.split(',')
            city = city.split("-")[0].strip()
            state = state.split("-")[0].strip()
            lookup_name = f"{city}, {state}"
            if lookup_name == "Winston, NC": lookup_name = "Winston-Salem, NC"
            if lookup_name == "Amherst Town, MA": lookup_name = "Amherst, MA"
            try:
                time.sleep(0.1)
                location = geolocator.geocode(lookup_name)
            except:
                print(f"Could not locate {lookup_name} aka {name}")
                exit()
            places.append((name, population, location.latitude, location.longitude))

    csv.writer(open("csa_and_cbsa.csv", "w", encoding='utf-8', newline='')).writerows(places)
