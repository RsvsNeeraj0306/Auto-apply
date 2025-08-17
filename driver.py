from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

options = Options()
options.add_argument(r"user-data-dir=C:\\Users\\pc\\AppData\\Local\\Microsoft\\Edge\\User Data")
options.add_argument("profile-directory=Default")
options.add_argument("start-maximized")
options.add_argument("disable-infobars") 
options.add_argument("--disable-extensions") 
options.add_argument("--disable-gpu")
options.add_argument('--no-sandbox')
options.add_argument('--log-level=3')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--enable-unsafe-swiftshader")
# options.add_argument("--headless")
service = Service(r'C:\Users\pc\Downloads\edgedriver_win64\msedgedriver.exe')

Driver = webdriver.Edge(service=service, options=options)
