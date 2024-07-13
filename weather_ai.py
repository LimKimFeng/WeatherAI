import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime, timedelta
import spacy
import random
import requests
import re

# Constants for time reference
TIME_NOW = "sekarang"
TIME_TODAY = "hari ini"
TIME_TOMORROW = "besok"
TIME_DAY_AFTER_TOMORROW = "lusa"
TIME_DAY_YESTERDAY = "kemarin"

class Ui_WelcomeWindow(object):
    def setupUi(self, WelcomeWindow):
        WelcomeWindow.setObjectName("WelcomeWindow")
        WelcomeWindow.resize(400, 300)
        self.centralwidget = QtWidgets.QWidget(WelcomeWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        font_title = QtGui.QFont()
        font_title.setPointSize(15)
        self.title.setFont(font_title)
        self.title.setObjectName("title")
        self.verticalLayout.addWidget(self.title)

        self.subtitle = QtWidgets.QLabel(self.centralwidget)
        font_subtitle = QtGui.QFont()
        font_subtitle.setBold(True)
        font_subtitle.setPointSize(10)
        self.subtitle.setFont(font_subtitle)
        self.subtitle.setObjectName("subtitle")
        self.verticalLayout.addWidget(self.subtitle)

        self.content = QtWidgets.QLabel(self.centralwidget)
        font_content = QtGui.QFont()
        font_content.setPointSize(8)
        self.content.setFont(font_content)
        self.content.setObjectName("content")
        self.verticalLayout.addWidget(self.content)

        self.button = QtWidgets.QPushButton(self.centralwidget)
        font_button = QtGui.QFont()
        font_button.setPointSize(10)
        self.button.setFont(font_button)
        self.button.setObjectName("button")
        self.verticalLayout.addWidget(self.button)

        self.verticalLayout.setSpacing(30)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)

        WelcomeWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(WelcomeWindow)
        QtCore.QMetaObject.connectSlotsByName(WelcomeWindow)

    def retranslateUi(self, WelcomeWindow):
        _translate = QtCore.QCoreApplication.translate
        WelcomeWindow.setWindowTitle(_translate("WelcomeWindow", "Weather AI"))
        self.title.setText(_translate("WelcomeWindow", "Weather AI"))
        self.subtitle.setText(_translate("WelcomeWindow", "Welcome to Weather AI User!"))
        self.content.setText(_translate("WelcomeWindow",
        "How to use:\n"
        "1. To get the current weather for a specific city, type: 'cuaca di [city]'.\n"
        "   Example: 'cuaca di Jakarta'\n"
        "2. To get the weather forecast for today or the next few days, type: 'cuaca di [city] [time]'.\n"
        "   Example: 'cuaca di Jakarta besok' or 'cuaca di Jakarta lusa'\n"                                         
        "3. If you don't specify a city, a random city will be chosen for you.\n"
        "4. Have fun and stay informed about the weather!"
        ))
        self.button.setText(_translate("WelcomeWindow", "Get Started"))


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 300)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        font_title = QtGui.QFont()
        font_title.setPointSize(15)
        self.title.setFont(font_title)
        self.title.setObjectName("title")
        self.verticalLayout.addWidget(self.title)

        self.chat = QtWidgets.QTextEdit(self.centralwidget)
        self.chat.setObjectName("chat")
        self.chat.setReadOnly(True)
        self.verticalLayout.addWidget(self.chat)

        self.user_input = QtWidgets.QLineEdit(self.centralwidget)
        font_input = QtGui.QFont()
        font_input.setPointSize(10)
        self.user_input.setFont(font_input)
        self.user_input.setObjectName("user_input")
        self.user_input.setPlaceholderText("Tanya cuaca....")
        self.verticalLayout.addWidget(self.user_input)

        self.verticalLayout.setContentsMargins(20, 20, 20, 20)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Weather AI"))
        self.title.setText(_translate("MainWindow", "Weather AI"))

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setMaximumSize(self.size())
        self.user_input.returnPressed.connect(self.handle_input)
        self.city = None

    def handle_input(self):
        user_message = self.user_input.text()
        self.chat.append(f"You: {user_message}")
        print("User input:", user_message)

        # Process input with spaCy
        doc = nlp(user_message)
        print("spaCy doc:", doc)

        city = None
        time = None
        weather_query = False

        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geopolitical entity (cities, countries, etc.)
                city = ent.text
                print("City:", city)

        if not city:
            # Fallback to regex if spaCy fails
            city_regex = re.search(r'cuaca di (\w+)', user_message, re.IGNORECASE)
            if city_regex:
                city = city_regex.group(1)
                print("City (regex):", city)

        for token in doc:
            if token.text.lower() in ["sekarang", "hari ini", "besok", "lusa", "kemarin"]:
                time = token.text.lower()
                print("Time:", time)
            if token.text.lower() == "cuaca":
                weather_query = True

        if weather_query:
            if not city and not self.city:
                city = self.random_city()
            elif not city and self.city:
                city = self.city
            if city:
                weather_info = self.get_weather_forecast(city, time)
                self.chat.append(f"AI: {weather_info}")
            else:   
                self.chat.append(f"AI: Saya tidak dapat mengenali kota yang dimaksud.")
        elif user_message == "":
            self.chat.append(f'AI: Coba input "cuaca"')
        else:
            self.chat.append(f"AI: Maaf, saya hanya dapat memberikan informasi cuaca.")

        self.user_input.clear()

    def random_city(self):
        cities = [
            "New York", "Los Angeles", "Tokyo", "Paris", "London", "Beijing", "Sydney", "Rio de Janeiro",
            "Moscow", "Berlin", "Mumbai", "Toronto", "Cairo", "Hong Kong", "Singapore", "Istanbul",
            "Bangkok", "Dubai", "Buenos Aires", "Rome", "San Francisco", "Seoul", "Shanghai", "Sao Paulo",
            "Mexico City", "Barcelona", "Jakarta", "Delhi", "Kuala Lumpur", "Chicago", "Miami",
            "Amsterdam", "Lisbon", "Vienna", "Athens", "Madrid", "Prague", "Brussels", "Zurich",
            "Stockholm", "Vancouver", "Montreal", "Dublin", "Helsinki", "Oslo", "Copenhagen",
            "Warsaw", "Budapest", "Munich", "Frankfurt", "Venice", "Milan", "Florence", "Naples",
            "Lyon", "Marseille", "Geneva", "Manchester", "Birmingham", "Glasgow", "Edinburgh",
            "Belfast", "Auckland", "Wellington", "Perth", "Melbourne", "Brisbane", "Cape Town",
            "Johannesburg", "Lagos", "Nairobi", "Casablanca", "Tunis", "Amman", "Beirut", "Doha",
            "Riyadh", "Jeddah", "Kuwait City", "Manama", "Muscat", "Karachi", "Lahore", "Islamabad",
            "Colombo", "Dhaka", "Kathmandu", "Yangon", "Hanoi", "Ho Chi Minh City", "Phnom Penh",
            "Vientiane", "Ulaanbaatar", "Tashkent", "Almaty", "Baku", "Yerevan", "Tbilisi",
            "Minsk", "Kiev", "Surabaya", "Bandung", "Medan", "Semarang", "Makassar", "Palembang", "Denpasar",
            "Padang", "Bogor", "Malang", "Yogyakarta", "Solo", "Banjarmasin", "Pontianak",
            "Balikpapan", "Samarinda", "Pekanbaru", "Batam", "Manado", "Kupang", "Mataram",
            "Jayapura", "Ambon", "Ternate", "Gorontalo", "Palu", "Kendari", "Bengkulu",
            "Pangkal Pinang", "Bandar Lampung", "Serang", "Cilegon", "Tangerang", "Depok",
            "Bekasi", "Cimahi", "Tasikmalaya", "Cirebon", "Madiun", "Probolinggo", "Kediri",
            "Blitar", "Jember", "Sidoarjo", "Tuban", "Gresik", "Mojokerto", "Magelang", "Purwokerto",
            "Salatiga", "Sragen", "Pekalongan", "Tegal", "Cilacap", "Sukabumi", "Garut", "Cianjur",
            "Majalengka", "Sumedang", "Kuningan", "Ciamis", "Banjar", "Subang", "Karawang", "Indramayu"
        ]
        random_city = random.choice(cities)
        if random_city:
            print("Random city:", random_city)
            return random_city
        else:
            return "Tidak ada kota yang tersedia"

    def get_weather_forecast(self, city, time=None) -> str:
        OPENWEATHER_API_KEY = "a97e71de587fcd767a39af05b1be15c6"
        if time in [TIME_NOW, TIME_TODAY, TIME_DAY_YESTERDAY, None]:
            OPENWEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
        else:
            OPENWEATHER_API_URL = "http://api.openweathermap.org/data/2.5/forecast"

        params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',
            'lang': 'id'
        }
        print("City detected:", city)

        response = requests.get(OPENWEATHER_API_URL, params=params)
        if response.status_code == 200:
            weather_data = response.json()
            forecast = self.parse_weather_data(weather_data, time)
            return forecast
        elif response.status_code == 404:
            return f"Kota {city} tidak ditemukan."
        else:
            print("OpenWeather response:", response)
            return f"Gagal mendapatkan data cuaca. Status code: {response.status_code}"

    def parse_weather_data(self, data, time):
        if time in [TIME_NOW, TIME_TODAY, TIME_DAY_YESTERDAY, None]:
            city = data['name']
            weather = data['weather'][0]['description']
            temperature = data['main']['temp']
            if time == TIME_DAY_YESTERDAY:
                forecast = f"Cuaca di {city} kemarin adalah {weather} dengan suhu {temperature}°C"
            else:
                forecast = f"Cuaca di {city} adalah {weather} dengan suhu {temperature}°C"
        else:
            city = data['city']['name']
            target_date = self.get_target_date(time)
            forecast = f"Gagal mendapatkan data cuaca untuk {city} pada {time}."
            for entry in data['list']:
                entry_date = datetime.fromtimestamp(entry['dt'])
                if entry_date.date() == target_date.date():
                    weather = entry['weather'][0]['description']
                    temperature = entry['main']['temp']
                    forecast = f"Cuaca di {city} {time} adalah {weather} dengan suhu {temperature}°C"
                    break
        return forecast

    def get_target_date(self, time):
        if time == TIME_TOMORROW:
            return datetime.now() + timedelta(days=1)
        elif time == TIME_DAY_AFTER_TOMORROW:
            return datetime.now() + timedelta(days=2)
        elif time == TIME_DAY_YESTERDAY:
            return datetime.now() - timedelta(days=1)
        else:
            return datetime.now()


class WelcomeWindow(QtWidgets.QMainWindow, Ui_WelcomeWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setMaximumSize(self.size())
        self.button.clicked.connect(self.open_main_window)

    def open_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    print("Python module:", sys.modules)
    print("Python version:", sys.version)
    print("Python platform:", sys.platform)
    sys.exit(app.exec_())
