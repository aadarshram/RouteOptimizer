# Route Optimizer for Google Maps

## Overview

Google Maps is the most popular service used by people all over the world to find locations, get directions and find the best route to their destinations. It includes a lot of amazing features such as traffic detection, estimated time taken to reach destination and whatnot. One shortcoming, however (or atleast I feel it is) is that if you desire to find a route plan to visit multiple locations, it asks you to fill the locations in the desired order and then gives the best route. This works for users who want to visit locations in some particular order but it is not always the case. Sometimes, you just want to visit all the desired locations but in the most optimal order. For this, you'll have to keep reviewing the route map and drag and reorder your stops until you think you have found a good order. I wanted a workaround for this. This gave birth to the idea of adding a Chrome Extension that takes in as input the locations you have filled in maps, finds an optimal order and displays back again in maps in the new optimal order. Now, i could have made a separate app or a website or such things but like I said, google maps is cool and this is the only thing that was bugging ,me. SO i decided to just narrow down my interest in tackling this specific issue.

## Concept
The idea is simple. When it comes to route optimization the first thing that comes to anyones mind is the Travelling Salesman problem (TSP) wherein theres a salesman who wants to make a round trip from a depot to a number of places and come back in the most optimal order. The scene can be represented as a graph- the locations are nodes and the routes connecting each locations ar edges. The cost associated with each decision, that is going from a given node to another through an edge connecting it is in a simple case proportional to the length of that edge or the distance between the locations in this case. Our problem can modelled as a TSP and then solved for usign any of your favourite methods to solve the standard TSP. I used Google's OR tools which has a TSP solver and works pretty well. I wasnt really interested in its intricate details just wanted a TSP solver, and google's is pretty good. Now, you might say TSP is only for round trips what if I want to go from point A to B and a number of places in between but not come back to A? Well, its simple, in your TSP problem just modfiy the cost associated with coming to your depot from any node as 0. Since there is np cost it does not affect your optimization so uou effectively end up with the best route from A to B. after making this solver using or tools and created an Api ysing FastAPI for this python code. The api takes as inpit whether it is round trip or not and the url of the fgoogle maps tab. Note that the url of the tab will ocntain the details of the locations you have input in its route input fields. SO you simply parse the url and get the addresses. The next step is to geocode the addresses to lat and lon coordinates for which I use an APi. This one is not so good at geocoding  but its free and for the purpose of demonstration its good enough. Then the cooridnates are used in the or tools, gives back a reordered list of coordinates and the api sends back a google maps directions url with the coordinates in the new order. The chrome extension uses a sevrice worker that sends input to the api gets the output url and opens it in a new tab.

## Project Structure

```
RouteOptimizer/
├── backend/
│   ├── main.py
│   ├── utils.py
│   ├── .env.example
│   ├── requirements.txt
├── RouteOptimizer_ChromeExt/
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── background.js
│   └── icon.png
├── .gitignore
└── README.md
```

## Setup Instructions

### Backend

1. **Install Dependencies**

   Navigate to the `backend/` directory and install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**

   Create a `.env` file in the `backend/` directory with the following content:

   ```
   API_KEY = your_actual_api_key_here
   ```

   You can get your geocoding api key from the service that I used [here](https://geocode.maps.co/). You just have to signup and get an access token. It has a Free Tier for 5000 requests/day which is more than sufficient. You can also explore other services, perhaps, better ones.
    **Note:** The `.env` file should not be committed to version control. Ensure it is included in `.gitignore`. 

3. **Run the FastAPI Server**

   Start the FastAPI server:

   ```bash
   fastapi run main.py
   ```

   The backend will be available at `http://0.0.0.0:8000`.
   You can take a look at the API docs [here](http://0.0.0.0:8000/docs)

### Chrome Extension

1. **Load the Extension**

   To test the Chrome extension, follow these steps:

   - Open Chrome and navigate to `chrome://extensions/`.
   - Enable "Developer mode" by toggling the switch in the top right corner.
   - Click "Load unpacked" and select the `RouteOptimizer_ChromeExt/` directory.

2. **Extension Files**

   - `manifest.json`: Defines the extension's metadata and permissions.
   - `popup.html`: The HTML layout for the popup interface.
   - `popup.js`: Handles interactions in the popup and communicates with the background script.
   - `background.js`: Manages background tasks and API requests.

## Usage

Navigate to the tab where you have Google maps with directions route filled

1. **Open the Chrome Extension**

   Click on the extension icon in the Chrome toolbar to open the popup.

2. **Enter Route Information**

   - Select whether the route is a round trip.
   - Click the "Find Optimal Route" button to send the data and solve for the best route.

3. **View Results**

   The extension will fetch the optimized route from the backend and open it in Google Maps in a new tab.

## Author

- **Aadarsh R**

For any queries or discussions you can write to me [here](www.linkedin.com/in/aadarsh-ramachandran-881a08293)

---
