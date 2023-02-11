#!/usr/bin/env python3

import requests
import os

def calculate_distance(origin, destination):
    #API_KEY = "YOUR_API_KEY"
    API_KEY = os.getenv("API_KEY")
    print(API_KEY)
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
city_list = ["Aalen", "Bietigheim", "Bruchsal", "Karlsruhe", "Lahr"]
html_table = generate_html_table(city_list)
print(html_table)