import pandas as pd
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
    Read file, format information and create new columns ('Name' and 'Year')
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
    except (GeocoderUnavailable, AttributeError):
        return None


def find_coordinates(films_data):
    '''
    Find coordinates and create new columns ('Latitude' and 'Longitude')
    '''
    films_data['Latitude'] = films_data['Location'].apply(find_latitude)
    films_data['Longitude'] = films_data['Location'].apply(find_longitude)
    films_data = films_data[films_data['Latitude'].notna()]
    films_data = films_data[films_data['Longitude'].notna()]
    return films_data


def main():
    '''Main function'''
    films_data = read_file('locations.list')
    year = input('Please enter a year you would like to have a map for: ')
    films_data = choose_year(year, films_data)
    films_data = find_coordinates(films_data)
    print(films_data)


if __name__ == '__main__':
    main()
    # from doctest import testmod
    # print(testmod())
