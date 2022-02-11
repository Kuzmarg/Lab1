"""Task2"""
import argparse
import math
import folium
import geopy

def argument_parsing():
    """The function parses the given arguments

    Returns:
        [argparse.Namespace]: contains the given arguments
    """
    parser = argparse.ArgumentParser(description='Input the year, coordinates, and the path')
    parser.add_argument('Year', type=int, help = "Release year")
    parser.add_argument('Latitude', type=float, help = 'Latitude of your location')
    parser.add_argument('Longitude', type=float, help = 'Longitude of your location')
    parser.add_argument('Path', type=str, help='Path to the file with data')
    return parser.parse_args()

def extract_location_name(line):
    """
    Gets the location name for geopy from the string
    Args:
        line (str): start line

    Returns:
        (str): name of the location
    """
    edited_line = sorted(line.split(')'), key = len)
    edited_line = sorted(edited_line[-1].split('('), key=len)
    return edited_line[-1].strip()


def parse_data(path, year, latitude, longtitude):
    """
    Parses the file with data and finds top10 closest places
    Args:
        path (str): string with path to the data file
        year (int): release year of the film
        latitude (float): latitude of the user
        longtitude (float): longitude of the user

    Returns:
        [list]: list of 10 or less elements
        Each element is a tuple of film name,
        coordinates and distance to the user
    (no doctest as the result depends on the data file and its location)
    """
    my_position = (latitude, longtitude)
    positions = []
    saved_locations = {}
    with open(path, 'r', encoding='utf-8', errors = 'ignore') as data:
        for line in data:
            line = line.strip()
            if str(year) in line:
                film = line[:line.find(str(year))-2]
                name = extract_location_name(line[line.find(str(year))+5:])
            else:
                continue


            if name not in saved_locations:
                try:
                    coordinates = find_location(name)
                except AttributeError:
                    continue
                saved_locations[name] = coordinates
            else:
                coordinates = saved_locations[name]
            distance = calc_distance(my_position,coordinates)


            is_in_list = False
            for check in positions:
                if coordinates == check[1]:
                    is_in_list = True


            if len(positions) < 10 and not is_in_list:
                positions.append((film,coordinates,distance))
                positions = sorted(positions, key=lambda x: x[2])
            elif not is_in_list and distance < positions[9][2]:
                del positions[9]
                positions.append((film,coordinates,distance))
                positions = sorted(positions, key=lambda x: x[2])

    return positions

def calc_distance(your_coord, point_coord):
    """
    Calculates distance in kilometres between 2 points
    Args:
        your_coord (tuple): coordinates of user
        point_coord (tuple): coordinates of user

    Returns:
        [float]: distance in kilometres
    >>> int(calc_distance((49.8397,24.0297),(50.9077,34.7981)))
    775
    """
    lat1 = your_coord[0] * math.pi / 180
    lat2 = point_coord[0] * math.pi / 180
    lon1 = your_coord[1] * math.pi / 180
    lon2 = point_coord[1] * math.pi / 180
    dist=2*6400*math.asin((math.sin((lat1-lat2)/2)**2+math.cos(lat1)*
    math.cos(lat2)*math.sin((lon1-lon2)/2)**2)**(1/2))
    return dist

def find_location(name):
    """
    Returns coordinates of a place
    Args:
        name (str): Name of the location

    Returns:
        [tuple]: coordinates
    # >>> find_location("Lviv")
    # (49.841952, 24.0315921)
    """
    location = geolocator.geocode(name)
    return location.latitude, location.longitude

def build_map(your_coord, positions):
    """
    Generates a map from your position and
    a list of tuples
    (film, coordinates) and
    saves it in html file.
    Args:
        tour_coord (tuple): tuple with user's coordinates

        positions (list): list of tuples
            with films' names and coordinates
    """
    map1 = folium.Map(location = your_coord, zoom_start = 10)
    fg1 = folium.FeatureGroup(name ='Locations of filming')
    fg2 = folium.FeatureGroup(name = 'Distance from you')
    fg3 = folium.FeatureGroup(name = 'Opposite points for fun')
    for loc in positions:
        lat = loc[1][0]
        lon = loc[1][1]
        oppos_lon = lon + 180 if lat < 0 else lon - 180
        oppose_lat = -lat
        fg3.add_child(folium.Marker(location = (oppose_lat, oppos_lon), popup = loc[0],
        icon = folium.Icon(color='red')))
        fg2.add_child(folium.Marker(location = loc[1], popup = f'Distance from you - {loc[2]}',
        icon = folium.Icon()))
        fg1.add_child(folium.Marker(location = loc[1], popup = loc[0], icon = folium.Icon()))
    map1.add_child(fg1)
    map1.add_child(fg2)
    map1.add_child(fg3)
    map1.add_child(folium.LayerControl())
    map1.save('map.html')


if __name__=='__main__':
    geolocator = geopy.geocoders.Nominatim(user_agent = 'Simplyname')
    import doctest
    doctest.testmod()
    args = argument_parsing()
    positions1 = parse_data(args.Path,args.Year,args.Latitude,args.Longitude)
    build_map((args.Latitude,args.Longitude), positions1)
