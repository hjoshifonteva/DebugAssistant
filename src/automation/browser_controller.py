from selenium import webdriver
from selenium.webdriver.common.by import By

class BrowserController:
    def __init__(self):
        self.driver = None
        
    async def setup(self):
        self.driver = webdriver.Chrome()