from city import *
from matplotlib import pyplot as plt

if __name__ == '__main__':
    cities = load_cities()
    cities.sort(key=lambda city: city.population, reverse=True)
    names = [i.name for i in cities]
    populations = [i.population for i in cities]
    plt.bar(names, populations)
    plt.show()
