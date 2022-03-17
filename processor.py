import requests
import json
import pandas as pd
import sys
import sqlite3
import urllib.parse
import datetime

# Globals
station_ids = []
valid_types = ["csv","json","sqllite","CSV","JSON"]

stationj = ""

gweather_data = pd.DataFrame([])

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

# get the past 152 of from a station (due to API limitations)
def load_observations(station="sni"):
    if station.upper() not in station_ids:
        print("Error! station " + str(station).upper() + " not a real station id.")
        print("Station ids should be 3 letters long")
        return
    observation_url = "https://api.weather.gov/stations/" + station + "/observations?"
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    then = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(7)

    dates = {
        "start":then.isoformat(),
        "end":now.isoformat(),
    }

    try:
        raw_data = requests.get(observation_url,params=dates)
    except Exception as e:
        print(e)
        return

    try:
        weather_data = pd.json_normalize(raw_data.json()['features'])
    except Exception as e:
        print(e)
        print("Possibly bad JSON request?")
        return

    # clean weather data:
    try:
        weather_data = weather_data.drop('properties.cloudLayers',axis=1)
        weather_data = weather_data.drop('properties.heatIndex.value',axis=1)
        weather_data = weather_data.drop('properties.visibility.value',axis=1)
        weather_data = weather_data.drop('properties.@type',axis=1)
        weather_data = weather_data.drop('properties.station',axis=1)
    except Exception as e:
        print (e)
        return

    print(weather_data)
    global gweather_data
    gweather_data = weather_data

def print_stations():
    stationj = get_stations()
    for station_object in stationj['features']:
        print(station_object['properties']['stationIdentifier'] + " : " + station_object['properties']['name'])

def save_data(filename="weather_data", dtype="csv"):
    if dtype not in ["sql","json","csv"]:
        print("error: " + str(dtype) + " not recognized")
        return
    real_filename = filename+"."+dtype
    global gweather_data
    if(dtype == 'sql'):
        real_filename = filename+'.db'

        connect = sqlite3.connect(real_filename)
        #print(gweather_data)
        gweather_data.applymap(str).to_sql("weatherDB",connect, if_exists='replace')
        connect.close()
    elif(dtype == 'csv'):
        gweather_data.to_csv(real_filename)
    else:
        gweather_data.to_json(real_filename)

    print("Saved to "+ real_filename +" at table weatherDB")
    return

def print_help():
    print("Commands Available")
    print("help\n   prints a list of  weather stations to add\n")
    print("stations\n   prints a list of  weather stations to add\n")
    print("load-obeservations\n   loads data from a weather station to use\n    useage: 'load-observations idOfWeatherStation\n     default value: SNI")
    print("save-data\n   saves data to a file\n      useage: 'save-data filename datatype'\n    valid types:'sql','json,'csv'; defaults are weatherdata.filetype and csv")

command_dict = {
    'help':print_help,
    'stations':print_stations,
    'load-observations':load_observations,
    'save-data':save_data
}

def main():
    stationj = get_stations()
    print("Welcome to Weather Station API  Processsor Command Prompt \n")
    print("""This program takes weather station data from the National Weather Sevice's API
and adds it to a JSON, sqllite, or CSV file.""")
    print("     For help type 'help'\n     To quit type 'quit' or press 'Ctrl-C'")
   # print_stations(stationj)
   # print(station_ids)
    command = [""]
    args = []

    # rudimentary shell
    while(command[0] != "quit"):
        try:
            command = input("weather >> ").split()
            if not command:
                command = [""]
            if len(command) > 1:
                args = command[1:]

        # quit if the user presses ctrl c
        except KeyboardInterrupt:
            sys.exit()
        # print exception as last resort
        except Exception as e:
            print(e)

        if command[0] in command_dict and len(args) == 1:
            command_dict[command[0]](str(args[0]))
        elif command[0] in command_dict and len(args) == 2:
            command_dict[command[0]](filename=str(args[0]),dtype=str(args[1]))
        elif command[0] in command_dict:
            command_dict[command[0]]()
        elif command[0] != "":
            print_help()
    sys.exit()
if __name__ == "__main__":
    main()
