# Film Map
 This program can generates HTML map of films of the selected year. This map has 4 layers:
 * **Main layer** - the map
 * **User location** - coordinates where are user
 * **Nearest film points** - locations of film creation closest to the user
 * **User`s film points** - location where selected film was created

## Purpose of this map
This map has many options for use. There are some ideas to use this map for movies lovers:
* Find what movies were made in your hometown and visit these places
* Plan your trip to visit places of creation your favorite film
* During travel find places of film creation near you

## How to use program
1. Download main.py and locations.lst
2. Install libraries from requirements.txt
3. Start function main() from main.py
4. Input year, coordinates and title of film
5. Wait 2-3 minutes while the map is being generated
6. Open map file in current directory

## Example of working program
```
Please enter a year you would like to have a map for: 2011
Please enter your location (format: lat, long): 49.8177029, 24.0237912
Please enter a film of this year: Game of Thrones
Map is generating...
Please wait...
Finished. Please have look at the map Game_of_Thrones_2011_film_map.html
```
![map_example](https://user-images.githubusercontent.com/44781809/108078136-f93de600-7075-11eb-97d8-dad1b3b654ae.jpg)
- ![#A7260A](https://via.placeholder.com/15/A7260A/000000?text=+) `user location`
- ![#DC20F1](https://via.placeholder.com/15/DC20F1/000000?text=+) `nearest points of film creation`
- ![#F1A120 ](https://via.placeholder.com/15/F1A120/000000?text=+) `place of creation selected film`

# Structure of HTML file
HTML-file consists of:
* **\<head\>** contains links and scripts
* **\<body\>** contains map
* **\<script\>** create marks on map
