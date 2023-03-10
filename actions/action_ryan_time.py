from datetime import datetime, date
import requests 

# this script calculates what day the user started the intervention
# thereby, tracks the days, weeks and months to provide tailored customization

# also tracks the time period of the day, season

# includes weather summary: go outside or not (is the most relevant for our users)
# but also offers users a choice if raining or snowing

#start date expected from digital enabler labels
start_year = 2023
start_month = 1
start_day = 25

def calcStart():
    global program_days
    startdate = date(start_year, start_month, start_day)
    today = date.today()

    diff = today - startdate 
    program_days = diff.days

    return program_days

calcStart()

#example usage...
if program_days == 0:
    print("Welcome to the program! It's your first day") #this is probably the best use case. 

def calcWeeksMonths():
    global user_week, user_month
    calcStart()
    user_week = int(program_days / 7) + 1 # +1 as we want ordinal number
    user_month = -(-user_week // 4) #rounded up... seems to work pretty well

    return user_week, user_month

calcWeeksMonths()

#example usage ...
if user_month == 2:
    print("Excellent going! It's now your second month of the program. Let's keep up the good work")

def getTime():
    global phase
    now = datetime.now()
    timeNow = int(now.strftime("%H"))
    if 4 <= timeNow < 11:
        phase = "Morning"
    elif 11 <= timeNow < 17:
        phase = "Daytime"
    elif 17 <= timeNow < 22:
        phase = "Evening"
    else:
        phase = "LateNight"
    return phase 

getTime()

#example usage ...
if phase == "Evening":
    print("It's time to unwind")
elif phase == "Daytime":
    print("Hope you're staying active!")

def getSeason(): #note this is tailored to Japan. June is usually the rainy season.
    global season
    currentMonth = datetime.now().month

    if 3 <= currentMonth < 6:
        season = 'spring'
    elif currentMonth == 6:
        season = 'rainy' 
    elif 7 <= currentMonth < 9:
        season = 'summer'
    elif 9 <= currentMonth < 11:
        season = 'autumn'
    else:
        season = 'winter'
    return season

getSeason()

#example usage ...
if season == "winter":
    print("Don't forget to wrap up warm")

def currentWeatherSummary(city):
    global weather_main
    """
    param city: the city based on user location
    returns: the weather forecast of the location
    """
    api_address = "http://api.openweathermap.org/data/2.5/weather?appid=0c42f7f6b53b244c78a418f4f181282a&q="
    # city = input('Enter the City Name :')
    url = api_address + city
    json_data = requests.get(url).json()

    weather_main = json_data['weather'][0]['main']   

    return weather_main

currentWeatherSummary('Sendai')

#example usage ...
if weather_main == 'Clear' or weather_main == 'Clouds':
    print("OK to go outside (depending on temperature)")
elif weather_main == 'Rain' or weather_main == 'Drizzle':
    print("")
    #"raining - up to you to go outside or not" #give user a choice. Can always say, "I'll stay in"
elif weather_main == 'Snow':
    #"snowing, up to you. Take care in slippery conditions"
    print("")
elif weather_main == 'Thunderstorm':
    #"heavy rain and thunderstorms. Advised to stay inside."
    print("")
else:
    #"Weather may be unpredictable, take care if going outside."
    print("")

