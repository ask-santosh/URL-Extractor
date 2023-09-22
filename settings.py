import chromedriver_autoinstaller
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

options = webdriver.ChromeOptions()
options.add_argument("headless")
# service = Service()

chromedriver_autoinstaller.install()

# cap = DesiredCapabilities().CHROME
# cap["marionette"] = False
