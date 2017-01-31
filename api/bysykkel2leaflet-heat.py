#!/usr/bin/env python
import configparser
import datetime
import json
import os.path
import sys
import urllib.request
from pprint import pprint

if __name__ == "__main__":
	config = configparser.ConfigParser()
	config.read("config.ini")

	api_url = config["default"]["api_url"]
	stations_url = api_url + "/stations"
	availability_url = api_url + "/stations/availability"
	
	save_folder = config["default"]["save_folder"]

	now = datetime.datetime.now().strftime("%Y%m%dT%H%M")

	leaflet_heat_json_path = os.path.join(save_folder, "leaflet_heat.json")
	leaflet_heatmap_json_path = os.path.join(save_folder, "leaflet_heatmap.json")
	leaflet_heatmap_json_datetime_path = os.path.join(save_folder, "leaflet_heatmap_%s.json" % now)

	stations = json.loads(urllib.request.urlopen(stations_url).read().decode("utf-8"))["stations"]
	availabilities = json.loads(urllib.request.urlopen(availability_url).read().decode("utf-8"))["stations"]

	leaflet_heat_data = []
	leaflet_heatmap_data = []

	max_value = 0

	# merge into single list
	for station in stations:
		if not station["ready"]:
			continue

		for availability in availabilities:
			if availability["id"] == station["id"]:
				station["availability"] = availability["availability"]

		latitude = station["center"]["latitude"]
		longitude = station["center"]["longitude"]
		value = station["availability"]["bikes"]

		if value > max_value:
			max_value = value
		
		leaflet_heat_data.append([latitude, longitude, value])
		leaflet_heatmap_data.append({"lat":latitude, "lng":longitude, "value":value})

	leaflet_heat_json = json.dumps(leaflet_heat_data)
	leaflet_heatmap_json = json.dumps({"max": max_value, "data": leaflet_heatmap_data})

	with open(leaflet_heat_json_path, "w") as f:
		f.write(leaflet_heat_json)
	with open(leaflet_heatmap_json_path, "w") as f:
		f.write(leaflet_heatmap_json)
	with open(leaflet_heatmap_json_datetime_path, "w") as f:
		f.write(leaflet_heatmap_json)
