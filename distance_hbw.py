#!/usr/bin/env python3

import requests
import os
import csv
import datetime

class StartAndDestination:
    def __init__(self, start_city, destination_city):
        self.start_city = start_city.strip()
        self.destination_city = destination_city.strip()

    def from_array(entries):
        return Voyage(entries[0], entries[1], entries[2], entries[3])

    def __hash__(self):
        return hash((self.start_city, self.destination_city))

    def __eq__(self, other):
        return (self.start_city, self.destination_city) == (other.start_city, other.destination_city)

    def __str__(self):
        return f"{self.start_city}, {self.destination_city}"

class Voyage:
    def __init__(self, start_city, destination_city, distance, duration):
        self.start_city = start_city.strip()
        self.destination_city = destination_city.strip()
        self.distance = distance
        self.duration = duration

    def from_array(entries):
        return Voyage(entries[0], entries[1], entries[2], entries[3])

    def get_csv_entry(self):
        return f"{self.start_city}; {self.destination_city}; {self.distance}; {self.duration}"

    def __str__(self):
        return f"{self.start_city}, {self.destination_city}, {self.distance}, {self.duration}"

def read_city_list():
    #return ["Aalen", "Bietigheim", "Bruchsal", "Karlsruhe", "Lahr"]
    result = []
    with open("hbw_cities.txt") as cities_file:
        lines = cities_file.readlines()
    for line in lines:
        result.append(line.strip())

    result.sort()    
    return result

def write_entries_to_file_cache(new_file_entries_to_write):

    now = f"; {datetime.datetime.utcnow()}"

    lines_to_write = []
    for entry in new_file_entries_to_write:
        lines_to_write.append(entry.get_csv_entry() + now + "\n")

    print(lines_to_write)    

    with open("distances.csv", "a") as cache_file:
        cache_file.writelines(lines_to_write)
        
def calculate_distance(origin, destination):
    #for testing witout paying:
    #return Voyage(origin, destination, "98", "4551")
    API_KEY = os.getenv("API_KEY")
    #print(API_KEY)
    '''
    we expect:
    {'destination_addresses': ['Bietigheim-Bissingen, Germany'], 
        'origin_addresses': ['Aalen, Germany'], 
        'rows': [{'elements': [
        {'distance': {'text': '98.2 km', 'value': 98167}, 
        'duration': {'text': '1 hour 18 mins', 'value': 4655}, 
        'status': 'OK'}]}], 
        'status': 'OK'} 
    '''
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={origin}&destinations={destination}&key={API_KEY}"
    response = requests.get(url)
    result = response.json()
    print(result)
    
    distance = result['rows'][0]['elements'][0]['distance']['value']
    duration = result['rows'][0]['elements'][0]['duration']['value']
    return Voyage(origin, destination, distance, duration)
    #return result['rows'][0]['elements'][0]['distance']['value']

def generate_html_table(city_list, cache_entries, field_selector = "distance"):
    #city_distances = {}
    # for start_city in city_list:
    #     city_distances[start_city] = {}
    #     for target_city in city_list:
    #         if start_city == target_city:
    #             city_distances[start_city][target_city] = 0
    #         else:

    #             city_distances[start_city][target_city] = calculate_distance(start_city, target_city)

    dummy_voyage = Voyage("same_city", "same_city", "0", "0")

    table = "<table>\n"
    table += "<tr>"
    table += "<th>City</th>"
    for start_city in city_list:
        table += "<th>{}</th>".format(start_city)
    table += "</tr>"

    for start_city in city_list:
        table += "<tr>"
        table += "<td>{}</td>".format(start_city)
        for target_city in city_list:
            start_and_destination = StartAndDestination(start_city, target_city)

            cache_entry = cache_entries.get(start_and_destination, dummy_voyage)
            value = "0"
            if field_selector == "distance":
                value = f"{int(float(cache_entry.distance) / 1000)} km"
            else:
                value = str(datetime.timedelta(seconds=int(cache_entry.duration)))
                value = value[:-3]

            table += "<td>{}</td>".format(value)
        table += "</tr>"
        table += "\n"

    table += "</table>"
    return table

# Example usage
city_list = read_city_list()
print(f"Checking the distances for the cities: {city_list}")
cache_file_name = "distances.csv"
cache_entries={}
with open (cache_file_name, "r") as cache_file:
    lines = cache_file.readlines()
    for line in lines:
        entries=line.split(";")
        start_and_destination = StartAndDestination(entries[0].strip(), entries[1].strip())
        cache_entry = cache_entries.get(start_and_destination, None)
        if not cache_entry:
            cache_entries[start_and_destination] = Voyage.from_array(entries)

#cache is updated, now check which cities we need
new_file_entries_to_write=[]
for start_city in city_list:
    for destination_city in city_list:
        start_and_destination = StartAndDestination(start_city, destination_city)
        if destination_city == start_city:
            continue
        if not cache_entries.get(start_and_destination, None):
            print(f"Need to retrieve distance for {start_and_destination} from google...")
            voyage = calculate_distance(start_city, destination_city)
            new_file_entries_to_write.append(voyage)
            cache_entries[start_and_destination]=voyage

write_entries_to_file_cache(new_file_entries_to_write)

html_table = generate_html_table(city_list, cache_entries)
print(html_table)
with open("distances.html", "w") as distance_file:
    distance_file.write(html_table)

html_table = generate_html_table(city_list, cache_entries, "duration")
print(html_table)
with open("duration.html", "w") as duration_file:
    duration_file.write(html_table)    