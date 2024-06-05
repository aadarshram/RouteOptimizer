'''
Trip Planner-

Objective: 
Given a set of locations to visit from a start point to an end point, constraints of time windows for the locations, total number of days in trip,
find the route plan with shortest distance cost to cover the locations and finish the trip. 

This real-life problem statement can be modelled as an extension to TSP.
'''

# Import libraries

import requests
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import folium
from itertools import pairwise
import webbrowser

def create_distance_matrix(coordinates):
    '''
    Create distance matrix (see 'create_data_model()')
    '''
    # Using OSRM distance matrix API
    base_url = "http://router.project-osrm.org/table/v1/driving/"
    # formatting 
    coords = ';'.join([f'{lon},{lat}' for lat, lon in coordinates])
    response = requests.get(f'{base_url}{coords}?annotations=distance')
    if response.status_code != 200:
        raise Exception('Error in API request')
    data = response.json()
    # or-tools requires integer entries in distance matrix. Since distance differences < 1m do not matter, we round of all distances in the matrix
    return [[round(element) for element in row] for row in data['distances']]

 
def create_data_model(coordinates, start_node, end_node):
    '''
    Create data model
    '''
    data = {}
    data['coordinates'] = coordinates
    data['start'] = start_node
    data['end'] = end_node

    data['distance_matrix'] = create_distance_matrix(data['coordinates'])
    # A distance matrix stores as ijth element the distance between node i and node j. 
    
    data['num_vehicles'] = 1 # In our case interested in one vehicle only.
    data['depot'] = 0 # All round trip, start and end location is depot.
    
    ''' Update req: User input for depot. Also option to choose round trip or end to end. If end to end incorporate TSP for end to end route plan. Implement'''

    return data

def solve_tsp(data):
    '''
    Solve the route optimization problem
    '''
    print('Solving.')
    # 'manager' is the index manager fior the routing model 'routing'.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot']) # args: (no. of nodes, no. of vehicles, start_end_index)
    # The manager takes care of all index <-> node conversions. We only need to deal with our nodes

    ''' Update req: Diff start and end location. '''

    # Create routing model
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index): # Nested fn.
        '''
        Distance callback: Takes from and to indices and returns distance between them. (for routing solver)
        This is the cost associated with an edge.
        '''
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return data['distance_matrix'][from_node][to_node]

    # register distance callback with solver
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # Set cost: We shall consider distance 
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index) 
    ''' Update: Customized cost considering other factors'''

    # # allow to drop nodes
    # for node in range(1, len(data['distance_matrix'])):
    #     routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    # Set search parameters and first solution strategy
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC)
    search_parameters.time_limit.seconds = 5 * 60 # 5 min time limit for the search
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC) # Sets a greedy path as initial

    ''' Update: Explore other first solution strategy. Check guided local search'''

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        index = routing.Start(0)
        plan_output = []
        while not routing.IsEnd(index):
            plan_output.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        plan_output.append(manager.IndexToNode(index))
    print('Done!')
    return manager, routing, solution, plan_output
    

def print_sol(manager, routing, solution):
    '''
    Print solution details
    '''
    if solution:
        
        print(f'Objective: {solution.ObjectiveValue()} m')
        # # Print dropped nodes
        # dropped_nodes = 'Dropped nodes:\n'
        # for node in range(routing.Size()):
        #     if routing.IsStart(node) or routing.IsEnd(node):
        #         continue
        #     if solution.Value(routing.NextVar(node)) == node: # if dropped,it points to itself
        #         dropped_nodes += f'{manager.IndexToNode(node)}'
        # print(dropped_nodes)
            
        index = routing.Start(0)
        route_plan = 'Route:\n'
        route_distance = 0
        while not routing.IsEnd(index):
            route_plan += f'{manager.IndexToNode(index)}->'

            ''' Update req: This prints node indices. Change to print location addresses'''

            prev_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(prev_index, index, 0)
        route_plan += f'{manager.IndexToNode(index)}\n'
        print(route_plan)
        print(f'Route distance: {route_distance/1000} km\n')
    return None

def display_on_map(coordinates):
    ''' 
    Function to view the optimized path on a map
    '''
    print('Creating map with locations.')
    # Adding markers
    
    map = folium.Map()
    folium.Marker(
            location = list(coordinates[0]),
            tooltip = 'Click here to view details of the place.',
            popup = f'node: 0 ; location: {coordinates[0]}',
            icon = folium.Icon(color = 'green', prefix = 'fa', icon = '0')
        ).add_to(map)

    for i, coord in enumerate(coordinates[1:-1]):
        folium.Marker(
            location = list(coord),
            tooltip = 'Click here to view details of the place.',
            popup = f'node: {i+1}; location: {coord}',
            icon = folium.Icon(color = 'red', prefix = 'fa', icon = f'{i+1}')
        ).add_to(map)
    print('Finding optimized route.')
    # request route
    coordinates = ';'.join([f'{lon},{lat}' for lat, lon in coordinates])
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{coordinates}?overview=full&alternatives=true&geometries=geojson"
    response = requests.get(osrm_url)
    data = response.json()

    route = data['routes'][0]['geometry']
    legs = data['routes'][0]['legs']
    len_legs = len(legs)
    for i, (start, end) in enumerate(pairwise(route['coordinates'])):
        distance = legs[i % len_legs]['distance'] / 1000
        locations = [(start[1], start[0]), (end[1], end[0])]
        folium.PolyLine(locations = locations, tooltip = 'Click here to view details of the route.', popup = f'Distance: {distance:.3f} km').add_to(map)
    # DIsplay map with appropriate zoom
    bounds = [[coord[1], coord[0]] for coord in route['coordinates']]
    map.fit_bounds(bounds)
    print('Done!')
    # Save and open map in browser
    map.save('map_display.html')
    webbrowser.open('map_display.html')
    return None

def main():

    # User input
    # coordinates = [
    # (52.5200, 13.4050),  # Berlin
    # (53.5511, 9.9937),   # Hamburg
    # (48.1351, 11.5820),  # Munich
    # (50.9375, 6.9603),   # Cologne
    # (50.1109, 8.6821)    # Frankfurt
    # ] # (lat, lon) list of tuples of locations to visit

    coordinates = [
    (52.5163, 13.3777),  # Brandenburg Gate
    (52.5218, 13.4132),  # Alexanderplatz
    (52.5250, 13.3685),  # Berlin Central Station
    (52.5194, 13.4010),  # Berlin Cathedral
    (52.5050, 13.4399)   # East Side Gallery
    ]
    ''' Update: user input location to coordinates function'''
    start_node = 0 # node index of the start point
    end_node = 3 # node index of the end point (wont work for now)
    #penalty = 10 ** 10 # cost of skipping a node

    # create the data model
    data = create_data_model(coordinates, start_node, end_node) 
    # solve the problem
    manager, routing, solution, route_plan = solve_tsp(data)
    # print solver status
    i = routing.status()
    if i == 0:
        print('ROUTING NOT SOLVED')
    elif i == 1:
        print('ROUTING SUCCESS')
    elif i == 2:
        print('ROUTING PARTIAL SUCCESS. LOCAL OPTIMUM NOT REACHED')
    elif i == 3:
        print('ROUTING FAIL')
    elif i == 4:
        print('ROUTING FAIL TIMEOUT')
    elif i == 5:
        print('ROUTING INVALID')
    elif i == 6:
        print('ROUTING INFEASIBLE')

    optimal_coords = [coordinates[i] for i in route_plan]
    
    
    # print solution details (if needed)
    p = input('Do you want to print solution details? (y/n)')
    if p == 'y':
        print_sol(manager, routing, solution)
    
    # display on map (if needed)
    m = input('Do you want to view the route on a map? (y/n)')
    if m == 'y':
        display_on_map(optimal_coords)
if __name__ == '__main__':
    main()


