# Route Optimizer for Google Maps

## Overview

Google Maps is an essential tool for navigation, offering a wide range of features such as traffic detection, estimated travel times, and turn-by-turn directions. However, when it comes to planning routes with multiple stops, it lacks the ability to automatically optimize the order of stops, if necessary. Typically, users must manually reorder stops to find the most efficient route.

This project provides a solution in the form of a Chrome extension that automatically optimizes the order of stops on Google Maps. The extension reads the locations from your route, calculates the optimal order, and reloads the map with the optimized route. Instead of developing a separate app or website, this extension improves the experience directly within Google Maps.

## Concept

This project leverages the Traveling Salesman Problem (TSP) as a foundation. The TSP involves finding the shortest possible route that visits all specified locations exactly once and returns to the starting point (in the case of a round trip). This problem is represented as a graph, where locations are nodes and the routes connecting them are edges. The weight of each edge corresponds to the distance between locations.

The project uses Google's [OR-Tools](https://developers.google.com/optimization/routing/tsp) to solve the TSP. Additionally, it supports both round-trip and one-way journeys by adjusting the cost associated with returning to the starting point. For one-way trips, the return cost is set to zero, effectively turning the problem into a shortest-path problem between the start and end locations.

### Key Features:

- **Route Optimization**: Automatically reorder your stops to find the most efficient route.
- **Round-trip and One-way Journeys**: Choose whether you want to optimize a round-trip or a one-way journey.
- **Integration with Google Maps**: The extension extracts route details from Google Maps and reloads the optimized route directly in the browser.
- **Backend Powered by FastAPI**: The optimization logic runs on a FastAPI backend that handles requests from the Chrome extension.
- **Geocoding API**: Addresses are converted to latitude and longitude coordinates using a geocoding API.

## Project Structure

```
RouteOptimizer/
├── backend/
│   ├── main.py               # FastAPI app with route optimization logic
│   ├── utils.py              # Helper functions and TSP solver
│   ├── .env.example          # Example environment variables file
│   ├── requirements.txt      # Python dependencies
├── RouteOptimizer_ChromeExt/  # Chrome extension files
│   ├── manifest.json          # Extension metadata and permissions
│   ├── popup.html             # HTML layout for the popup interface
│   ├── popup.js               # JavaScript for popup interactions
│   ├── background.js          # Background script for handling API requests
│   └── icon.png               # Extension icon
├── .gitignore                 # Ignoring sensitive and unnecessary files
└── README.md                  # Project documentation
```

## Setup Instructions

### Backend Setup

1. **Install Dependencies**

   Navigate to the `backend/` directory and install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**

   - Create a `.env` file in the `backend/` directory with the following content:
   
     ```bash
     API_KEY=your_actual_api_key_here
     ```

   - Replace `your_actual_api_key_here` with your geocoding API key. You can obtain an API key from [Geocode Maps](https://geocode.maps.co/). They offer a free tier with up to 5,000 requests/day, which is sufficient for testing and small-scale use. You can also try other alternatives as this (or atlleast its free tier) does not work well for some locations.

   **Important**: Ensure that the `.env` file is listed in `.gitignore` to prevent accidentally committing sensitive information to version control.

3. **Run the FastAPI Server**

   Start the FastAPI server:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

   The backend will be available at `http://0.0.0.0:8000`. You can view the automatically generated API documentation at [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs).

### Chrome Extension Setup

1. **Load the Extension**

   To load the Chrome extension:

   - Open Chrome and navigate to `chrome://extensions/`.
   - Enable "Developer mode" by toggling the switch in the top right corner.
   - Click "Load unpacked" and select the `RouteOptimizer_ChromeExt/` directory.
   - The extension will be visible on the page. Toggle the enable switch and reload it once.

2. **Extension Files**

   - `manifest.json`: Defines the extension's metadata and permissions.
   - `popup.html`: The HTML layout for the popup interface.
   - `popup.js`: Handles interactions in the popup and sends data to the backend.
   - `background.js`: Manages background tasks and API requests.

## Usage

1. **Prepare Google Maps**

   Open Google Maps and enter the locations you want to visit in the directions input fields.

2. **Open the Chrome Extension**

   Click on the extension icon or its name from the extensions list in the Chrome toolbar to open the popup.

3. **Configure the Route**

   - Choose whether the route is a round trip or one-way by selecting the appropriate option.
   - Click the "Find Optimal Route" button to send the data to the backend for optimization.

4. **View Results**

   The extension will fetch the optimized route from the backend and open it in a new Google Maps tab with the reordered stops.

## Security Considerations

- **Environment Variables**: Store sensitive information like API keys in environment variables, and ensure they are not included in your codebase. The `.env` file should be listed in your `.gitignore`.
- **CORS Settings**: The backend is configured to allow requests from Chrome extensions. For production, you should further restrict access to specific extensions for better security.

## Author

- **Aadarsh R**

For any queries or discussions, feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/aadarsh-ramachandran-881a08293).

--- 