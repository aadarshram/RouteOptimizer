# Contains utility functions for the route optimizer
import requests
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def parse_url(url):
    '''
    Function to parse Google Maps url to retrieve route location addresses
    '''
    url = url.split('/')
    dir_index = url.index('dir')
    address_list = url[dir_index+1:-2]
    return address_list

def get_coordinates(address):
    '''
    Get coordinates from address of location
    '''
    try: # check if already coordinates
        data = address.split(',')
        return (float(data[0]), float(data[1]))
    except:
        response = requests.get(f'https://nominatim.openstreetmap.org/search?q={address}&format=json')
        if response:
            data = response.json()
            return (float(data[0]['lat']), float(data[0]['lon']))
        else:
            raise ValueError(f'Some problem with response {response.json()}')

def _fetch_distance_matrix(base_url, coords):
    response = requests.get(f'{base_url}{coords}?annotations=distance')
    data = response.json()
    return [[round(element) for element in row] for row in data['distances']]

def _create_distance_matrix(coordinates):
    base_url = "http://router.project-osrm.org/table/v1/driving/"
    coords = ';'.join([f'{lon},{lat}' for lat, lon in coordinates])
    distance_matrix = _fetch_distance_matrix(base_url, coords)
    return distance_matrix

def create_data_model(coordinates, depot):
    data = {}
    data['coordinates'] = coordinates
    data['distance_matrix'] = _create_distance_matrix(coordinates)
    data['num_vehicles'] = 1
    data['depot'] = depot
    return data

def solve_tsp(data, isRoundTrip):
    distance_matrix = data['distance_matrix']
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        if (to_node == 0) and (not isRoundTrip): return 0 # If not round trip
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC
    search_parameters.time_limit.seconds = 10 * 60
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        index = routing.Start(0)
        plan_output = []
        while not routing.IsEnd(index):
            plan_output.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        plan_output.append(manager.IndexToNode(index))
        return plan_output

    return None

def get_optimized_route(url, isRoundTrip):
    '''
    Function to find optimal route
    '''
    address_list = parse_url(url) # Get addresses from Google Maps url
    coordinates_list = [get_coordinates(address) for address in address_list] # Get coordinates from addresses
    # Find optimized route
    depot = 0 # Start location (and end if round trip)
    data = create_data_model(coordinates_list, depot)
    plan_output = solve_tsp(data, isRoundTrip)
    if plan_output:
        opt_route = [coordinates_list[node] for node in plan_output]
        return opt_route
    return None

if __name__ == '__main__':
    url = input()
    print(get_optimized_route(url, True))

