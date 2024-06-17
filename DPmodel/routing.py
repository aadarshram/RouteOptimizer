'''
Trip Planner-

Objective: 
Given a set of locations to visit from a start point to an end point, constraints of time windows for the locations, total number of days in trip,
find the route plan with shortest distance cost to cover the locations and finish the trip. 

This real-life problem statement can be modelled as an extension to TSP.
'''

# Import necessary libraries

import requests
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from sklearn.cluster import KMeans
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp


def get_coordinates(address):
    '''
    Get coordinates given address
    '''
    api_key = '511b0be98ff5cff47206ed794d8e99bf'

    response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={address}&limit=1&apiid={api_key}')
    data = response.json()
    print(data)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if data:
            return tuple([data[0]['lat'], data[0]['lon']])
        else:
            return None
    return None

# Helper functions

async def fetch_distance_matrix(session, base_url, coords):
    '''
    Fetch distance_matrix from API (see 'create_distance_matrix()')
    '''
    async with session.get(f'{base_url}{coords}?annotations=distance') as response:
        if response.status != 200:
            raise Exception('Error in API request')
        data = await response.json()
    # or-tools requires integer entries in distance matrix. Since distance differences < 1m do not matter, we round of all distances in the matrix
    return [[round(element) for element in row] for row in data['distances']]

 
async def create_distance_matrix(coordinates):
    '''
    Create distance matrix (see 'create_data_model()')
    '''
    # Using OSRM distance matrix API
    base_url = "http://router.project-osrm.org/table/v1/driving/"
    # formatting 
    coords = ';'.join([f'{lon},{lat}' for lat, lon in coordinates])
    async with aiohttp.ClientSession() as session:
        distance_matrix = await fetch_distance_matrix(session, base_url, coords)
    return distance_matrix
 
def create_data_model(coordinates, depot, num_days):
    '''
    Create data model
    '''
    data = {}
    data['coordinates'] = coordinates
    #data['start'] = start_node
    #data['end'] = end_node    
    data['num_vehicles'] = 1 # In our case interested in one vehicle only.
    data['depot'] = depot # All round trip, start and end location is depot.
    data['num_days'] = num_days
    ''' Update req: Also option to choose round trip or end to end. If end to end incorporate TSP for end to end route plan. Implement'''

    return data

def find_clusters(data):
    '''
    CLuster the locations based on num_days
    '''
    k = data['num_days']

    nodes = data['coordinates'][:]
    del nodes[0]

    # depot
    node_0 = data['coordinates'][data['depot']]

    # perform k-means
    kmeans = KMeans(n_clusters = k)
    kmeans.fit(nodes)
    cluster_labels = kmeans.labels_

    all_cluster_data = []
    for i in range(k):
        cluster_data = [node_0] + [nodes[j] for j, label in enumerate(cluster_labels) if label == i] # depot goes to all clusters
        all_cluster_data.append(cluster_data)
    return all_cluster_data


def solve_tsp(data, distance_matrix):
    '''
    Solve the route optimization problem
    '''

    # 'manager' is the index manager fior the routing model 'routing'.
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), data['num_vehicles'], data['depot']) # args: (no. of nodes, no. of vehicles, start_end_index)
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

        return distance_matrix[from_node][to_node]

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
    search_parameters.time_limit.seconds = 10 * 60 # 10 min time limit for the search
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
        return manager, routing, solution, plan_output
    
    return None, None, None, None
    
def solve_cluster(data, cluster_data):

    try: 
        cluster_distance_matrix = asyncio.run(create_distance_matrix(cluster_data))
        manager, routing, solution, plan_output = solve_tsp(data, cluster_distance_matrix)
        if solution:
            return manager, routing, solution, plan_output
    except Exception as e:
        print(f'Error occured for cluster {cluster_data} : {e}')
    return None

def solver(data, all_cluster_data):

    sol_data =[]
    with ThreadPoolExecutor() as exec: # solve for all clusters parallely
        futures = [exec.submit(solve_cluster, data, cluster_data) for cluster_data in all_cluster_data]
        for future in futures:
            result = future.result()
            if result is not None:
                sol_data.append(result)
    return sol_data

def print_sol(sol_data, opt_route):
    '''
    Print solution details
    '''
    # for i in range(len(sol_data)):
    #     manager, routing, solution, plan_output = sol_data[i]
    #     if solution:
            
    #         print(f'Objective: {solution.ObjectiveValue()} m')
    #         # # Print dropped nodes
    #         # dropped_nodes = 'Dropped nodes:\n'
    #         # for node in range(routing.Size()):
    #         #     if routing.IsStart(node) or routing.IsEnd(node):
    #         #         continue
    #         #     if solution.Value(routing.NextVar(node)) == node: # if dropped,it points to itself
    #         #         dropped_nodes += f'{manager.IndexToNode(node)}'
    #         # print(dropped_nodes)
                
    print('-' * 20)

    for i in range(len(sol_data)):
        _,_,solution,_ = sol_data[i]
        print(f'Cluster {i+1} : Route distance: {solution.ObjectiveValue() / 1000} km')
        print('Route:', "->".join(map(str, opt_route[i])))
        print('-' * 20)

    return None

def display_on_map(opt_route): # folium is not working
    ''' 
    Function to view the optimized path on a map
    '''
    print('Creating map with locations.')
  
    # Encode locations
    for i,route in enumerate(opt_route):
        print("-" * 15)
        route = [f'{coord[0]},{coord[1]}' for coord in route]
        full_url = f'https://www.google.com/maps/dir/?api=1&origin={route[0]}&destination={route[-1]}&waypoints={"|".join(route[1:-1])}'
        print(f'View cluster {i+1}: {full_url}')

    # webbrowser.open(full_url)
    return None



def main():

    #User input
    # coordinates = [
    # (52.5200, 13.4050),  # Berlin
    # (53.5511, 9.9937),   # Hamburg
    # (48.1351, 11.5820),  # Munich
    # (50.9375, 6.9603),   # Cologne
    # (50.1109, 8.6821)    # Frankfurt
    # ] # (lat, lon) list of tuples of locations to visit

    add = True
    address_list = []
    coordinates = []
    while add:
        address = input('Input address of a location')
        address_list.append(address)
        loc = get_coordinates(address)
        print(loc)
        coordinates.append(loc)
        add = input('Add more? (y/n)')
        if add == 'y':
            add = True
        else:
            add = False


    # coordinates = [
    # (52.5163, 13.3777),  # Brandenburg Gate
    # (52.5218, 13.4132),  # Alexanderplatz
    # (52.5250, 13.3685),  # Berlin Central Station
    # (52.5194, 13.4010),  # Berlin Cathedral
    # (52.5050, 13.4399)   # East Side Gallery
    # ]
    ''' Update: user input location to coordinates function'''
    #start_node = 0 # node index of the start point
    #end_node = 3 # node index of the end point (wont work for now)
    depot = int(input(f'Enter index of depot (Within 0 - {len(coordinates)})')) # node index of depot
    #penalty = 10 ** 10 # cost of skipping a node
    num_days = int(input(f'Enter number of days of trip (Less than {len(coordinates)})'))
    # create the data model
    data = create_data_model(coordinates, depot, num_days) 

    split = True
    while split:
        print('Splitting into clusters')
        # Split locations for each day visit
        all_cluster_data = find_clusters(data)
        print('Solving')
        # Solve the problem
        sol_data = solver(data, all_cluster_data)
        print('Done!')
        # print solver status
        # routing_status = {0:'ROUTING NOT SOLVED', 
        #                   1:'ROUTING SUCCESS', 
        #                   2:'ROUTING PARTIAL SUCCESS. LOCAL OPTIMUM NOT REACHED', 
        #                   3:'ROUTING FAIL', 
        #                   4:'ROUTING FAIL TIMEOUT', 
        #                   5:'ROUTING INVALID', 
        #                   6:'ROUTING INFEASIBLE'}
        # for i in range(len(sol_data)):
        #     routing = sol_data[i][1]
        #     status = routing.status()
            # print(routing_status[status])
        opt_route = []
        for i in range(len(sol_data)):
            route_plan = sol_data[i][3]
            optimal_route_per_cluster = [all_cluster_data[i][j] for j in route_plan]
            opt_route.append(optimal_route_per_cluster)
        
        
        # print solution details (if needed)
        p = input('Do you want to print solution details? (y/n)')
        if p == 'y':
            print_sol(sol_data, opt_route)

        split = input('Try again for a better plan? (y/n)')
        if split == 'y':
            split = True
        else:
            split = False
        print('-' * 20)
    print('Optimal route finalized')
    print('-' * 20)

    # display on map (if needed)
    m = input('Do you want to view the route on a map? (y/n)')
    if m == 'y':
        display_on_map(opt_route)
    print('-' * 20)

if __name__ == '__main__':
    main()

