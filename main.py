import requests
import os
from openai import OpenAI
import json
from datetime import datetime
import pyttsx3


class Config:
  """ Configuration class.
  """

  def __init__(self):
    self.openai_api_key = 'XXXXXXXXXX'
    self.openai_model = "gpt-3.5-turbo-0125"
    self.openweathermap_api_url = "http://api.openweathermap.org/data/2.5/weather"
    self.openweathermap_api_key = "XXXXXXXXXX"
    self.latitude = 00.00000
    self.longitude = 00.00000
    self.name = "John Doe"
    self.prompt = "Give ma a greeting message tells me the time and weather. keep is really short (like a start message at the bootup), make it german. also make it usable for a text to speach program."
    self.text_to_speech = True
    self.speech_rate = 200
    self.speech_volume = 0.9

  def load(self):
    """ Load configuration from a file.
    """
    path = "~/win-greeter-config.json"
    # escape windows home path
    path = os.path.expanduser(path)
    if os.path.exists(path):
      with open(path, "r") as f:
        data = json.load(f)
        self.openai_api_key = data.get("openai_api_key", self.openai_api_key)
        self.openai_model = data.get("openai_model", self.openai_model)
        self.openweathermap_api_url = data.get("openweathermap_api_url", self.openweathermap_api_url)
        self.openweathermap_api_key = data.get("openweathermap_api_key", self.openweathermap_api_key)
        self.latitude = data.get("latitude", self.latitude)
        self.longitude = data.get("longitude", self.longitude)
        self.name = data.get("name", self.name)
        self.prompt = data.get("prompt", self.prompt)
        self.text_to_speech = data.get("text_to_speech", self.text_to_speech)
        self.speech_rate = data.get("speech_rate", self.speech_rate)
        self.speech_volume = data.get("speech_volume", self.speech_volume)
    else:
      self.save()

  def save(self):
    """ Save configuration to a file.
    """
    path = "~/win-greeter-config.json"
    # escape windows home path
    path = os.path.expanduser(path)
    with open(path , "w+") as f:
      data = {
        "openai_api_key": self.openai_api_key,
        "openai_model": self.openai_model,
        "openweathermap_api_url": self.openweathermap_api_url,
        "openweathermap_api_key": self.openweathermap_api_key,
        "latitude": self.latitude,
        "longitude": self.longitude,
        "name": self.name,
        "prompt": self.prompt,
        "text_to_speech": self.text_to_speech,
        "speech_rate": self.speech_rate,
        "speech_volume": self.speech_volume
      }
      json.dump(data, f, indent=2)


class WeatherData:
  """ Class to store weather data.
  """

  def __init__(self, weather, temperature, wind_speed_ms, wind_direction_deg):
    self.weather = weather
    self.temperature = temperature
    self.wind_speed_ms = wind_speed_ms
    self.wind_speed_kmh = int(round(wind_speed_ms * 3.6 * 10)) / 10
    self.wind_direction_deg = wind_direction_deg
    self.wind_direction = self.degrees_to_compass(wind_direction_deg)

  def to_string(self):
    return f"Weather: {self.weather}\nTemperature: {self.temperature}°C\nWind Speed: {self.wind_speed_kmh} km/h\nWind Direction: {self.wind_direction}"

  def degrees_to_compass(self, deg):
    """ Convert wind direction degrees to compass direction.
    """
    compass_directions = ["North", "NorthNorthEast", "NorthEast", "EastNorthEast", "East", "EastSouthEast", "SouthEast", "SouthSouthEast",
                          "South", "SouthSouthWest", "SouthWest", "WestSouthWest", "West", "WestNorthWest", "NorthWest", "NorthNorthWest"]
    index = round(deg / 22.5) % 16
    return compass_directions[index]


class App:
  """ Main application class.
  """

  def __init__(self):
    self.config = Config()
    self.config.load()
    self.openAiClient = OpenAI(api_key=self.config.openai_api_key)
    self.speach_engine = pyttsx3.init()

  def openai_request(self, prompt):
    """ Send a request to OpenAI's API and return the response.
    """
    completion = self.openAiClient.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages= [{
        "role": "user",
        "content": prompt
      }],
    )
    ai_response = completion.choices[0].message.content
    return ai_response

  def get_current_weather(self):
    """ Get the current weather data from OpenWeatherMap API.
    """
    url = f"{self.config.openweathermap_api_url}?lat={self.config.latitude}&lon={self.config.longitude}&appid={self.config.openweathermap_api_key}&units=metric"
    response = requests.get(url)
    jj = response.json()

    if response.status_code == 200:
      weather = jj['weather'][0]['description']
      temperature = jj['main']['temp']
      wind_speed_ms = jj['wind']['speed']
      wind_deg = jj['wind']['deg']
      data = WeatherData(weather, temperature, wind_speed_ms, wind_deg)
      return data
    else:
      return None

  def text_to_speech(self, text):
    self.speach_engine.setProperty('rate', 200)
    self.speach_engine.setProperty('volume', 0.9)
    self.speach_engine.say(text)
    self.speach_engine.runAndWait()

  def run(self):
    """ Run the main application.
    """
    weather_data = self.get_current_weather()
    prompt = self.config.prompt
    prompt += "\nMyName: " + self.config.name
    prompt += "\nDateTime: " + datetime.now().strftime("%Y-%M-%d %H:%M")
    if weather_data:
      prompt += weather_data.to_string()
    else:
      prompt += "Error fetching weather data."
    ai_response = self.openai_request(prompt)
    print(ai_response)
    if self.config.text_to_speech:
      self.text_to_speech(ai_response)


###########################################################################

if __name__ == "__main__":
  app = App()
  app.run()
