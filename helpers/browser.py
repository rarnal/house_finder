from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutExceptiond

from requests_html import HTMLSession


class Browser:
    def __init__(self):
        self.session = None
        self.tries = 5
        self.url = None

        self.create_session()

    def create_session(self):
        pass

    def can_request(self):
        if not self.session:
            raise Exception("No session is opened")
        return True


class Selenium(Browser):

    def create_session(self):
        self.session = webdriver.Firefox()
    
    def get(self, url):
        if self.can_request():
            self.url = url
            self.session.get(url)

    def can_find_class(self, class_):
        err = 0
        
        while err < self.tries:
            try:
                WebDriverWait(self.session, 5).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, class_)
                    )
                )
            except:
                err += 1
                self.get(self.url)
            else:
                return True

        return False
        
    def get_content(self):
        return self.session.page_source


class Request_html(Browser):

    def create_session(self):
        self.session = HTMLSession(mock_browser=True)

    def get(self, url):
        if self.can_request():
            self.request = self.session.get(url)

    def can_find_class(self, class_):
        err = 0

        while err < self.tries:
            
            if not self.request.html.find('.{}'.format(class_)):
                err += 1
            else:
                return True

        return False

    def get_content(self):
        return self.request.content


