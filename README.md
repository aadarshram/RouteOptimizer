# Trip Planner

## Objective

The Trip Planner model aims to optimize route planning for a set of locations, given the total number of days in the trip. This real-life problem can be modeled as an extension of the Traveling Salesman Problem (TSP).

## Features

- Accepts user input for multiple locations.
- Converts location addresses to geographical coordinates using the OpenWeatherMap Geocoding API.
- Clusters locations based on the number of days in the trip using the KMeans algorithm.
- Solves the TSP for each cluster using Google's OR-Tools.
- Provides optimized routes and allows users to view them on Google Maps.

## Requirements

- Python 3.x
- Requests
- Scikit-learn
- OR-Tools
- aiohttp

Install the required libraries using the following command:
```bash
pip install requests scikit-learn ortools aiohttp
