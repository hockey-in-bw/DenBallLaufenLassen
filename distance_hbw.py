#!/usr/bin/env python3

import requests
import os
import csv

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
        self.distance = distance.strip()
        self.duration = duration.strip()

    def from_array(entries):
        return Voyage(entries[0], entries[1], entries[2], entries[3])

    def get_csv_entry(self):
        return f"{self.start_city}, {self.destination_city}, {self.distance}, {self.duration}\n"

    def __str__(self):
        return f"{self.start_city}, {self.destination_city}, {self.distance}, {self.duration}"

def read_from_google(start_and_destination):
    return Voyage(start_and_destination.start_city, start_and_destination.destination_city, "98", "4551")

def write_entries_to_file_cache(new_file_entries_to_write):
    lines_to_write = []
    for entry in new_file_entries_to_write:
        lines_to_write.append(entry.get_csv_entry())

    print(lines_to_write)    

    with open("distances.csv", "a") as cache_file:
        cache_file.writelines(lines_to_write)
        
def calculate_distance(origin, destination):
    API_KEY = os.getenv("API_KEY")
    print(API_KEY)
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
    return result['rows'][0]['elements'][0]['distance']['value']

def generate_html_table(city_list):
    city_distances = {}
    for start_city in city_list:
        city_distances[start_city] = {}
        for target_city in city_list:
            if start_city == target_city:
                city_distances[start_city][target_city] = 0
            else:
                city_distances[start_city][target_city] = calculate_distance(start_city, target_city)

    table = "<table>"
    table += "<tr>"
    table += "<th>City</th>"
    for start_city in city_distances:
        table += "<th>{}</th>".format(start_city)
    table += "</tr>"

    for start_city in city_distances:
        table += "<tr>"
        table += "<td>{}</td>".format(start_city)
        for target_city in city_distances:
            distance = city_distances[start_city][target_city]
            table += "<td>{}</td>".format(distance)
        table += "</tr>"

    table += "</table>"
    return table

# Example usage
s_u_d_1 = StartAndDestination("wurst", "brot")
s_u_d_2 = StartAndDestination("wurst", "brot")
if s_u_d_1 == s_u_d_2:
    print("it works")
else:
    print("it does not")    

city_list = ["Aalen", "Bietigheim", "Bruchsal", "Karlsruhe", "Lahr"]
cache_file_name = "distances.csv"
cache_entries={}
with open (cache_file_name, "r") as cache_file:
    lines = cache_file.readlines()
    for line in lines:
        entries=line.split(",")
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
            voyage = read_from_google(start_and_destination)
            new_file_entries_to_write.append(voyage)

write_entries_to_file_cache(new_file_entries_to_write)

exit()        
read_from_cache_or_api(city_list)
html_table = generate_html_table(city_list)
print(html_table)