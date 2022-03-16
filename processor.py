import requests
import json
import pandas
import sys

# Globals
station_ids = []
valid_types = ["csv","json","sqllite","CSV","JSON"]



def get_stations():
    station_url = 'https://api.weather.gov/stations?limit=500'
    try:
        station_response = requests.get(station_url)
    except Exception as e:
        print(e)
        print("Closing program, can not reach: 'https://api.weather.gov/stations'")
        quit()

    for station in station_response.json()['features']:
        station_ids.append(station['properties']['stationIdentifier'])
    return station_response.json()

def print_stations(stations_json):
    for station_object in stations_json['features']:
        print(station_object['properties']['stationIdentifier'] + " : " + station_object['properties']['name'])

def get_valid_input(message = "", valid_list = []):
    valid = False
    while (valid == False):
        user_raw = input(message)
        stripped = user_raw.strip()
        if len(valid_list) > 0 and stripped not in valid_list:
            print("Error! Valid inputs are:")
            for v in valid_list:
                print("'"+ v, end="', ")
                print("")
        else:
            valid = True
            return stripped


def print_help():
    print("Commands Available")
    print("help\n   prints a list of  weather stations to add\n")
    print("stations\n   prints a list of  weather stations to add\n")


command_dict = {
    'help':print_help,
    'stations':print_stations
}

def main():
    print("Welcome to Weather Station API  Processsor Command Prompt \n")
    print("""This program takes weather station data from the National Weather Sevice's API
and adds it to a JSON, sqllite, or CSV file.""")
    print("     For help type 'help'\n     To quit type 'quit' or press 'Ctrl-C'")
    stationj = get_stations()
    command = [""]
    args = []
    while(command[0] != "quit"):
        try:
            command = input("").split()
            if not command:
                command = [""]
            if len(command) > 1:
                args = command[1:]
            if command[0] in command_dict:
                command_dict[command[0]]()
            elif command[0] != "":
                print_help()

        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            print(e)

    sys.exit()
if __name__ == "__main__":
    main()
