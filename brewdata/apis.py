import requests
import json
import logging

url = "http://localhost:5000"

def getTemperatureData(channel = 1):

    try:

        if channel <  1:
            url = "http://localhost:5000"
        else:
            url = "http://picam:5000"

        url = "http://localhost:5000"
        #url = "http://localhost:5000"

        path = "/datapoint/" + str(channel)
        myResponse = requests.get(url + path)

        # For successful API call, response code will be 200 (OK)
        if (myResponse.ok):

            # Loading the response data into a dict variable
            # json.loads takes in only binary or string variables so using content to fetch binary content
            # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
            jData = json.loads(myResponse.content)

            return jData['value']
        else:
            # If response code is not ok (200), print the resulting http error code with description
            myResponse.raise_for_status()
    except:
        pass

    logging.error("Unable to get temperature data at: %s", url + path)

    return None

def getProgramName():
    return "Multistep Mash"

def getValueArray(sensor = 1, rows = 5, interleave = 1):

    try:

        url = "http://pibrew:5000"

        path = "/datapoints/" + str(sensor) + "/" + str(rows) + "/" + str(interleave)
        myResponse = requests.get(url + path)

        # For successful API call, response code will be 200 (OK)
        if (myResponse.ok):

            # Loading the response data into a dict variable
            # json.loads takes in only binary or string variables so using content to fetch binary content
            # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
            jData = json.loads(myResponse.content)

            return jData
        else:
            # If response code is not ok (200), print the resulting http error code with description
            myResponse.raise_for_status()
    except:
        pass

    logging.error("Unable to get values at: %s", url + path)

    return None

