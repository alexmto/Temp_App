import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty
from kivy.uix.button import Button
from kivy.network.urlrequest import UrlRequest
from kivy.uix.popup import Popup


class AddLocationForm(BoxLayout):
    search_input = ObjectProperty()
        
    def search_location(self):
        search_template = "http://api.openweathermap.org/data/2.5/find?q={}&type=like&APPID=8dfb3a7f5617a392458498142ba92a28"
        search_url = search_template.format(self.search_input.text)
        content = Button(text="Success! Tap here to dismiss this message.")
        popup = Popup(title='HELLO!', title_color=[0.3,0.6,1,1], 
                      title_align='center', content=content, 
                      auto_dismiss=False, size_hint=(None, None), 
                      size=(500, 200))
        
        content.bind(on_press=popup.dismiss)

        popup.open()
        request = UrlRequest(search_url, self.found_location)

    def found_location(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        cities = [(d['name'], d['sys']['country']) for d in data['list']]
        self.search_results.item_strings = cities
        self.search_results.adapter.data.extend(cities)
        self.search_results._trigger_reset_populate()

    def args_converter(self, index, data_item):
        city, country = data_item
        return {'location': (city, country)}

class LocationButton(ListItemButton):
    location = ListProperty()

class WeatherRoot(BoxLayout):
    current_weather = ObjectProperty()
    def show_current_weather(self, location = None):
        self.clear_widgets()

        if self.current_weather is None:
            self.current_weather = CurrentWeather()

        if location is not None:
            self.current_weather.location = location

        self.current_weather.update_weather()
        self.add_widget(self.current_weather)

    def show_add_location_form(self):
        self.clear_widgets()
        self.add_widget(AddLocationForm())

class CurrentWeather(BoxLayout):
    location= ListProperty(['Berlin', 'DE'])
    conditions= ObjectProperty()
    temp= NumericProperty()
    temp_min= NumericProperty()
    temp_max= NumericProperty()
    conditions_box = ObjectProperty()
    conditions_desc = StringProperty()
    wind = NumericProperty()
    conditions_image = StringProperty()

    def update_weather(self):
        config = WeatherApp.get_running_app().config
        temp_type = config.getdefault("General", "temp_type", "metric").lower()
      
        content = Button(text="Success! Tap here to dismiss this message.")
        popup = Popup(title='HELLO!', content=content, auto_dismiss=True, size_hint=(None, None), size=(500, 200))
        content.bind(on_press=popup.dismiss)
        popup.open()
        weather_template = "http://api.openweathermap.org/data/2.5/" + "weather?q={},{}&units={}&APPID=8dfb3a7f5617a392458498142ba92a28"
        weather_url = weather_template.format(
            self.location[0],
            self.location[1],
            temp_type)                                              
        request = UrlRequest(weather_url, self.weather_retrieved)
        
    def weather_retrieved(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        self.conditions_desc = data['weather'][0]['description']
        self.temp = data['main']['temp']
        self.temp_min = data['main']['temp_min']
        self.temp_max = data['main']['temp_max']
        self.wind = data['wind']['speed']
        self.conditions_image = "http://openweathermap.org/img/w/{}.png".format(data['weather'][0]['icon'])
       
class WeatherApp(App):
    def build_config(self, config):
        config.setdefaults('General', {'temp_type': "Metric"})
    def build_settings(self, settings):
        settings.add_json_panel("Weather Settings", self.config, data="""
            [
                {"type": "options",
                    "title": "Temperature System",
                    "section": "General",
                    "key": "temp_type",
                    "options": ["Metric", "Imperial"]
                }
            ]"""
            )
    def on_config_change(self, config, section, key, value):
        if config is self.config and key == "temp_type":
            try:
                self.root.children[0].update_weather()
            except AttributeError:
                pass

if __name__ == '__main__':
    WeatherApp().run()
