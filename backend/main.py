# FastAPI backend
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from utils import get_optimized_route
from typing import Dict, List



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["chrome-extension://*"],
    allow_methods = ["*"],
    expose_headers = ["Access-Control-Allow-Origin"]
)

@app.post("/")
async def root(request: Request):
    data = await request.json()
    url = data.get('url')
    isRoundTrip = data.get('roundTrip')
    output = get_route(url, isRoundTrip)
    maps_url = get_maps(output, isRoundTrip)
    return {"google_maps_url": maps_url}

def get_route(url: str, isRoundTrip: bool) -> Dict:
    output = get_optimized_route(url, isRoundTrip)
    return output

def get_maps(coordinates: List[List[float]], isRoundTrip: bool) -> str:
    if not coordinates or len(coordinates) < 2:
        return "Invalid"
    
    origin = f"{coordinates[0][0]}, {coordinates[0][1]}"
    destination = f"{coordinates[-2 + isRoundTrip][0]}, {coordinates[-2+ isRoundTrip][1]}"
    if len(coordinates) > 2:
        waypoints = "|".join([f"{coord[0]},{coord[1]}" for coord in coordinates[1:-2 + isRoundTrip]])
    else:
        waypoints = ""

    maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
    if waypoints:
        maps_url += f"&waypoints={waypoints}"

    return maps_url