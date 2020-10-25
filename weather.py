# Simple CLI weather script using MET.NO
#
# prlg September 11, 2020

import sys
import json
import requests
import maya


TEST_RED = '\u001b[31m'
TEST_GREEN = '\u001b[32m'
TEST_YELLOW = '\u001b[33m'
TEST_BLUE = '\u001b[34m'
TEST_FUSCHIA = '\u001b[35m'
TEST_SKYBLUE = '\u001b[36m'
TEST_GREY = '\u001b[37m'
TEST_SLATE = '\u001b[38;5;8m'
TEST_ORANGE = '\u001b[38;5;12m'
TEST_ENDC = '\u001b[0m'

complete_url = "https://api.met.no/weatherapi/locationforecast/2.0/complete"
compact_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
latitude = round(44.953667, 4)
longitude = round(-93.15922, 4)
payload = {'lat': latitude, 'lon': longitude}

metno_api = requests.get(compact_url, params=payload)
weather = json.loads(metno_api.text)

# Added for debugging; remove before done.
def jsonPrettyString(uglyString):
    return json.dumps(uglyString, indent=4, sort_keys=True)

# quick and easy time conversion dependent on TZ -- WIP, need to enhance for autodetection
def convertToSaneTime(isoTime, timeZone):
    return maya.MayaDT.from_iso8601(isoTime).datetime(to_timezone=timeZone, naive=True)

# Converts to Fahrenheit from Celsius, or opposite if Bool = False
def convertTemperature(temperatureIn, toF):
    if toF:
        temperatureF = (temperatureIn * 1.8) + 32
        return round(temperatureF, 1)
    else:
        temperatureC = (temperatureIn - 32) / (1.8)
        return round(temperatureC, 1)

# iterate across the full weather series
def loopWeatherSeries(weatherSeries):
    index = 0
    for series in weatherSeries:
        index+=1
        # print(series)
        print(index)
        print(convertToSaneTime(series['time'], 'US/Central'))

def getWeatherFromSeries(weatherSeries):
    currentWeather = weatherSeries[0]
    avgCloud, avgWind, highTemp, lowTemp = getFutureUpdates(weatherSeries)
    weatherDetails = currentWeather['data']['instant']['details']
    cloudCover = getCloudCover(weatherDetails['cloud_area_fraction'])
    windDirection = getDirection(weatherDetails['wind_from_direction'])
    windSpeed = translateWindSpeed(weatherDetails['wind_speed'])
    temp = convertTemperature(weatherDetails['air_temperature'], True)
    time = convertToSaneTime(currentWeather['time'], 'US/Central')
    printTemp(temp)
    printWind(windDirection, windSpeed)
    printColor(cloudCover, TEST_SLATE)
    printColor(averageClouds(avgCloud), TEST_SLATE)
    printExtremeTemp(convertTemperature(highTemp, True), True)
    printExtremeTemp(convertTemperature(lowTemp, True), False)
    print('\n\n')
    

def getFutureUpdates(weatherSeries):
    # willRain = False
    cloudTotal = 0
    avgCloud = 0
    windTotal = 0
    avgWind = 0
    highTemp = 0
    lowTemp = 100
    i = 0
    for series in weatherSeries:
        if i < 12:
            weatherDetails = series['data']['instant']['details']
            cloudTotal += weatherDetails['cloud_area_fraction']
            windTotal += weatherDetails['wind_speed']
            if weatherDetails['air_temperature'] > highTemp:
                highTemp = weatherDetails['air_temperature']
            if weatherDetails['air_temperature'] < lowTemp:
                lowTemp = weatherDetails['air_temperature']
            i += 1
        else:
            avgCloud = cloudTotal / 12
            avgWind = windTotal / 12
            return avgCloud, avgWind, highTemp, lowTemp

def averageClouds(clouds):
    if clouds <= 20:
        return "\nThe next 12 hours will see clear skies."
    elif clouds <= 60:
        return "\nShould be partially cloudy for a bit."
    elif clouds <= 80:
        return "\nIt's going to be cloudy."
    else:
        return "\nThere will be total cloud cover for the next 12 hours."

def printExtremeTemp(temperatureIn, isHigh):
    print('\n')
    if isHigh:
        printColor("12-hour High: ", TEST_GREY)
    else:
        printColor("12-hour Low: ", TEST_GREY)
    tempString = str(temperatureIn) + "F"
    printColor(tempString, tempSev(temperatureIn))

def printTemp(temperatureIn):
    print('\n')
    printColor("Current Temperature: ", TEST_GREY)
    tempString = str(temperatureIn) + "F"
    printColor(tempString, tempSev(temperatureIn))

def printWind(direction, speed):
    windString = direction + " Currently " + str(speed) + " MPH."
    print('\n')
    printColorLn(windString, TEST_ORANGE)
    print()

def getCloudCover(clouds):
    if clouds <= 20:
        return "We have mostly clear skies."
    elif clouds <= 60:
        return "Partially cloudy."
    elif clouds <= 80:
        return "It's a cloudy day."
    else:
        return "There's total cloud cover."

def tempSev(tempToCheck):
    if tempToCheck < 45:
        return TEST_SKYBLUE
    elif tempToCheck < 75:
        return TEST_GREEN
    elif tempToCheck > 74:
        return TEST_RED

def printColor(text, color):
    print(color, text, TEST_ENDC, sep='', end='')

def printColorLn(text, color):
    print(color, text, TEST_ENDC)

def translateWindSpeed(windSpeed):
    return round((windSpeed * 2.236936), 1)

def getDirection(direction):
    if direction < 23:
        return "A North wind blows."
    elif direction < 68:
        return "Nordeast."
    elif direction < 113:
        return "Eastern wind."
    elif direction < 158:
        return "The wind is blowing from the Southeast."
    elif direction < 203:
        return "A Southern wind blows."
    elif direction < 248:
        return "The wind blows from the Southwest."
    elif direction < 293:
        return "From the west, blows this wind."
    elif direction < 338:
        return "a Northwest wind is blowing."
    elif direction < 355:
        return "Two scholars rock fresh, North by Northwest (wind)"
    else:
        return "A North wind blows."

# print(jsonPrettyString(weather))
getWeatherFromSeries(weather['properties']['timeseries'])

