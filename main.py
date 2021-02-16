'''
This module create map with:
* your location
* nearest points of film creation
* location of creation selected film
'''

import math
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable

geolocator = Nominatim(user_agent="main")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)


def find_year(line: str) -> str:
    '''
    Find and return year of creating film from line
    >>> find_year('Harry Potter and the Chamber of Secrets (2002)')
    '2002'
    >>> find_year('Haunted (2014/IV)')
    '2014'
    >>> find_year('"#15SecondScare" (2015) {It is Me Jessica (#1.5)}')
    '2015'
    '''
    try:
        bracket = line.index('(')
        return line[bracket+1 : bracket+5]
    except ValueError:
        return None


def find_name(line: str) -> str:
    '''
    Find and return name of film from line
    >>> find_name('Harry Potter and the Chamber of Secrets (2002)')
    'Harry Potter and the Chamber of Secrets'
    >>> find_name('"#15SecondScare" (2015) {It is Me Jessica (#1.5)}')
    '#15SecondScare'
    '''
    try:
        bracket = line.index('(')
        line = line[:bracket-1]
        if line[0] == '"' and line[-1] == '"':
            line = line[1:-1]
        return line
    except (ValueError, IndexError):
        return None


def read_file(path: str) -> pd.DataFrame:
    '''
    Read file, delete unnecessary information and divide column "Name" on name and year
    '''
    films_data = pd.read_csv(path, sep = '\t+', skiprows = 14, \
        names=['Name', 'Location', 'Info'], engine='python')
    films_data = films_data.drop(columns = ['Info'])
    films_data['Year'] = films_data['Name'].apply(find_year)
    films_data['Name'] = films_data['Name'].apply(find_name)
    films_data = films_data.drop_duplicates()
    return films_data


def choose_year(year:str, films_data: pd.DataFrame) -> pd.DataFrame:
    '''
    Return the DataFrame with film created in input year
    '''
    films_data = films_data[films_data['Year'] == year]
    return films_data


def find_latitude(point: str) -> float:
    '''
    Find and return latitude of point
    >>> find_latitude('England, UK')
    52.5310214
    >>> find_latitude('Germany')
    51.0834196
    '''
    try:
        location = geolocator.geocode(point)
        return location.latitude
    except (GeocoderUnavailable, AttributeError):
        return None


def find_longitude(point: str) -> float:
    '''
    Find and return longitude of place
    >>> find_longitude('England, UK')
    -1.2649062
    >>> find_longitude('Germany')
    10.4234469
    '''
    try:
        location = geolocator.geocode(point)
        return location.longitude
    except (GeocoderUnavailable, AttributeError, ValueError):
        return None


def find_coordinates(films_data: pd.DataFrame) -> pd.DataFrame:
    '''
    Find coordinates and create new columns ('Latitude' and 'Longitude')
    '''
    films_data['Latitude'] = films_data['Location'].apply(find_latitude)
    films_data['Longitude'] = films_data['Location'].apply(find_longitude)
    films_data = films_data[films_data['Latitude'].notna()]
    films_data = films_data[films_data['Longitude'].notna()]
    return films_data


def find_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    '''
    Find distance between two points by coordinates
    >>> round(find_distance(49.8177029, 24.0237912, 49.2204274, 28.3793954), -2)
    321300.0
    >>> find_distance(5.0, 600.0, 5.0, 600.0)
    0.0
    '''
    radius = 6371e3
    radian_lat1 = lat1 * math.pi/180
    radian_lat2 = lat2 * math.pi/180
    delta_lat = (lat2-lat1) * math.pi/180
    delta_lon = (lon2-lon1) * math.pi/180

    haversine = math.sin(delta_lat/2) * math.sin(delta_lat/2) + \
            math.cos(radian_lat1) * math.cos(radian_lat2) * \
            math.sin(delta_lon/2) * math.sin(delta_lon/2)
    haversine = 2 * math.atan2(math.sqrt(haversine), math.sqrt(1-haversine))
    haversine = radius * haversine

    return haversine


def count_distance_to_point(lat: float, lon: float, films_data: pd.DataFrame) -> pd.DataFrame:
    '''
    Create new column 'Distance' which represented
    distance between user point and points in dataframe
    '''
    films_data['Distance'] = films_data.apply(lambda x: \
        find_distance(x['Latitude'], x['Longitude'], lat, lon), axis = 1)
    return films_data


def find_nearest(films_data: pd.DataFrame) -> pd.DataFrame:
    '''
    Return 10 nearest points where films were created
    '''
    films_data = films_data.sort_values(by=['Distance'])
    return films_data.head(10)


def find_locations_of_film(film: str, films_data: pd.DataFrame) -> pd.DataFrame:
    '''
    Return all locations where inputed film was created
    '''
    films_data = films_data[films_data['Name'] == film]
    return films_data


def create_layer_of_user_location(user_lan:float, user_lon:float) -> folium.FeatureGroup:
    '''
    Create layer with mark which represent user location
    '''
    user_location = folium.FeatureGroup(name="Your location")
    user_location.add_child(folium.Marker(location=[user_lan, user_lon], \
        popup='You are here', icon=folium.Icon(color='darkred')))

    return user_location


def create_layer_of_nearest(points:pd.DataFrame) -> folium.FeatureGroup:
    '''
    Create layer with 10 marks which represent nearest location where films were created
    '''
    film_names = points['Name']
    latitude = points['Latitude']
    longitude = points['Longitude']

    nearest_marks = folium.FeatureGroup(name="Nearest film points")
    for name, lat, lon in zip(film_names, latitude, longitude):
        nearest_marks.add_child(folium.Marker(location=[lat, lon], \
            popup=name, icon=folium.Icon(color='purple')))

    return nearest_marks


def create_layer_of_film_location(film: str, points: pd.DataFrame) -> folium.FeatureGroup:
    '''
    Create layer with marks which represent all location where the film was created
    '''
    location = points['Location']
    latitude = points['Latitude']
    longitude = points['Longitude']

    film_marks = folium.FeatureGroup(name=film)
    for point, lat, lon in zip(location, latitude, longitude):
        film_marks.add_child(folium.Marker(location=[lat, lon], \
            popup=point, icon=folium.Icon(color='orange')))

    return film_marks


def generate_file_name(year: str, film:str) -> str:
    '''
    Generate the name of map file
    >>> generate_file_name('2002', 'Harry Potter')
    'Harry_potter_2002_film_map.html'
    '''
    film = film.replace(' ', '_')
    map_name = film + '_' + year + '_film_map.html'
    return map_name


def create_map(user: folium.FeatureGroup, near: folium.FeatureGroup, films: folium.FeatureGroup, \
    map_name: str) -> None:
    '''
    Create a map with marks of your location, nearest film points and locations of entered film
    '''
    film_map = folium.Map()
    film_map.add_child(user)
    film_map.add_child(near)
    film_map.add_child(films)
    film_map.add_child(folium.LayerControl())
    film_map.save(map_name)


def main():
    '''Main function'''
    films_data = read_file('locations.list')

    year = input('Please enter a year you would like to have a map for: ')
    user_lan, user_lon = input('Please enter your location (format: lat, long): ').split(', ')
    film = input('Please enter a film of this year: ')

    print('Map is generating...')
    print('Please wait...')

    films_data = choose_year(year, films_data)
    films_data = find_coordinates(films_data)

    user_lan = float(user_lan)
    user_lon = float(user_lon)
    user_location_layer = create_layer_of_user_location(user_lan, user_lon)

    films_data = count_distance_to_point(user_lan, user_lon, films_data)
    nearest_films = find_nearest(films_data)
    nearest_layer = create_layer_of_nearest(nearest_films)

    film_locations = find_locations_of_film(film, films_data)
    film_layer = create_layer_of_film_location(film, film_locations)

    map_name = generate_file_name(year, film)
    create_map(user_location_layer, nearest_layer, film_layer, map_name)
    print(f'Finished. Please have look at the map {map_name}')

# Example:
# 2011
# 49.8177029, 24.0237912
# Game of Thrones

if __name__ == '__main__':
    main()
