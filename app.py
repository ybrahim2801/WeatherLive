# (c) 2024 Paul Ybrahim Caballes and Charlotte Cabal
# This program is a terminal-based weather viewer.

import os
import json
import time
from datetime import datetime

import requests
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import track
from rich.console import Console
from term_image.image import Size, from_file
from rich import print as show

OPTIONS = ["1", "2", "3"]
WEST_PACIFIC = "https://www.ssd.noaa.gov/jma/wpac/vis-l.gif"
BASE_API = "https://api.openweathermap.org/data/2.5/weather"
key = ""
latitude = 10.6521
longitude = 124.8526

def progress_bar(description, sleep=0.03):
    Console().clear()  # this will clear the screen
    for _ in track(range(20), description=description):
        time.sleep(sleep)
    Console().clear()

def main_menu():
    message = "[b][blue] WeatherLive[/blue]: Terminal-based Weather Forecaster.[/b]"
    show(Panel(message, expand=False))
    show("\n[b]MAIN MENU[/b]")
    show("[1] Change coordinates")
    show("[2] View weather map")
    show("[3] Exit")

def get_coordinates():
    global latitude
    global longitude

    coordinates = {}
    try:
        with open("coordinates.json") as file:
            coordinates = json.load(file)
    except:
        return change_coordinates()
    latitude = coordinates.get("latitude", 10.7460)
    longitude = coordinates.get("longitude", 124.7946)

def change_coordinates():
    global latitude
    global longitude

    show()
    show(Panel("[b]Change Coordinates[/b]", expand=False))
    latitude = float(input("Enter latitude: "))
    longitude = float(input("Enter longitude: "))

    coordinates = {"latitude": latitude, "longitude": longitude}
    with open("coordinates.json", mode="w+", encoding="utf-8") as file:
        file.write(json.dumps(coordinates))

def get_formatted_datetime(timestamp, formatting):
    return datetime.fromtimestamp(timestamp).strftime(formatting)

def set_weather_api_key():
    global key

    show()
    show(Panel("[b]Change API key[/b]", expand=False))
    key = input("Enter your weather API key: ")

def load_weather_data():
    if not key:
        return set_weather_api_key()

    URL = f"{BASE_API}?lat={latitude}&lon={longitude}&units=metric&appid={key}"
    response = requests.get(URL).json()

    location = response.get("name")
    country = response.get("sys").get("country")
    date = get_formatted_datetime(response.get("dt"), "%Y-%m-%d %I:%S %p")
    sunrise = get_formatted_datetime(response.get("sys").get("sunrise"), "%I:%S %p")
    sunset = get_formatted_datetime(response.get("sys").get("sunset"), "%I:%S %p")
    weather = response.get("weather")[0].get("main")
    description = response.get("weather")[0].get("description").title()
    temperature = float(response.get("main").get("temp"))
    humidity = response.get("main").get("humidity")
    wind = response.get("wind").get("speed")

    color1 = "grey53"
    color2 = "white"
    if "sky" in weather.lower():
        color1 = "yellow"
    elif "cloud" in weather.lower():
        color1 = "white"
        color2 = "blue"
    if 25 <= temperature < 30:
        color2 = "yellow"
    elif temperature >= 30:
        color2 = "red"

    message = f"[green underline]{location}, {country}[/green underline]\n" \
              f"[white]{date}[/white]\n\n" \
              f"[{color1}]{weather} [{color2}]{temperature}°C[/{color2}]\n" \
              f"[italic][grey53]> {description}[/italic]\n\n" \
              f"[white]Humidity: {humidity}%\n" \
              f"Wind: {wind} km/h\n" \
              f"Sunrise: {sunrise}\n" \
              f"Sunset: {sunset}"

    show(Panel(message, expand=False))

def download_map(filepath):
    if os.path.exists(filepath):
        return

    response = requests.get(WEST_PACIFIC, timeout=30)
    if response.status_code != 200:
        show("\n[red]ERROR:[/red] Failed to download map.")
        input("Hit ENTER key to continue...")
        return

    with open(filepath, "wb") as file:
        file.write(response.content)

def view_weather_map(filepath):
    download_map(filepath)
    print(from_file(filepath, width=50))
    input("Press ENTER to continue...")

def main():
    dt = datetime.now().strftime("%Y-%m-%d")
    filepath = f"{dt}.png"

    progress_bar("Loading...")
    while True:
        main_menu()
        selected = Prompt.ask("Select", choices=OPTIONS, show_choices=False)

        if selected == "1":
            change_coordinates()
        elif selected == "2":
            load_weather_data()
            view_weather_map(filepath)
        elif selected == "3":
            Console().clear()
            print("[red]\nClosing the program... Goodbye!")
            break

    Console().clear()


if __name__ == "__main__":
    main()
