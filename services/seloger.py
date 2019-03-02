import sqlite3
import datetime
import requests
import time

from bs4 import BeautifulSoup
from helpers.browser import Request_html as Browser

from config import seloger
from config import general
from helpers.sql import SQLite

# https://www.seloger.com/list.htm?types=1,2&projects=2,5&enterprise=0&natures=1,2,4&price=NaN/300000&places=[{cp:75}]&qsVersion=1.0
# https://www.seloger.com/list.htm?idtypebien=2,1&pxMax=300000&idtt=2,5&naturebien=1,2,4&cp=84


class ServiceSeloger:
    def __init__(self):
        self.db = general.DATABASE
        self.page = 0
        self.session = Browser()
        self.log_pages = False

    def refresh_database(self, project=None, types=None, cp=[75]):
        
        # HARD RESET !! Delete and recreate table 
        # self.delete_table()
        # self.create_table()
        page = 1

        for code in cp:
            self.page = 0
            origin_url = self.build_url(project, types, code)
            url = self.turn_and_add_page(origin_url)

            print("Starting to check for zip code {}".format(origin_url))
            content = self.get_content(origin_url)
            soup = BeautifulSoup(content, 'html.parser')

            error = 0
            while self.page <= 100:
                page += 1
                
                if self.log_pages:
                    with open("logs/{}.txt".format(page), "w") as f:
                        f.write(soup.prettify())

                print("checking pages {}".format(url))

                if not soup.find_all('div', class_="c-pa-list"):
                    print("Nothing useful was found...")
                    break
                else:
                    error = 0
                    print("Extracting data...")
                    self.extract_and_register_content(soup)
                
                    url = self.turn_and_add_page(origin_url)
                    content = self.get_content(url)
                    soup = BeautifulSoup(content, 'html.parser')

    def turn_and_add_page(self, url):
        self.page += 1
        url += "&{}={}".format(seloger.PAGE_URL, self.page)
        return url
        
    def extract_and_register_content(self, soup):
        nodes = soup.find_all('div', class_="c-pa-list")
        
        for node in nodes:
            try:
                data = self.extract_data(node)
            except:
                continue

            if not self.check_if_exist('URL', data['URL']):
                try:
                    print("Saving data...")
                    self.register_data(data)
                except Exception as e:
                    print("Not saved :(")
                    print(e)
                    pass
            else:
                print("Already exists !")

        return True

    def check_if_exist(self, col, val):

        request = "SELECT * FROM seloger WHERE {}='{}'".format(col, val)

        with SQLite(self.db) as cursor:
            cursor.execute(request)
            if cursor.fetchall():
                return True
            return False


    def register_data(self, data):

        request = """
        INSERT INTO seloger
            (date, project, type, city, zip_code, size, price, rooms, 
             bedrooms, URL)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        params = (
            datetime.date.today().isoformat(),
            data['project'],
            data['type'],
            data['city'],
            data['zip_code'],
            data['size'],
            data['price'],
            data['rooms'],
            data['bedrooms'],
            data['URL'],
        )

        with SQLite(self.db) as cursor:
            cursor.execute(request, params)
        return True

    def extract_data(self, node):
        data = {}
        data['URL'] = node.find('a', class_='c-pa-link').get('href')

        data['rooms'] = int(node.find('div', class_='h-fi-pulse')
                                .get('data-nb_pieces'))
        if node.find('div', class_='h-fi-pulse').get('data-nb_chambres'):
            data['bedrooms'] = int(node.find('div', class_='h-fi-pulse')
                                       .get('data-nb_chambres'))
        else:
            data['bedrooms'] = '0'
        data['size'] = float(node.find('div', class_='h-fi-pulse')
                                 .get('data-surface').replace(',', '.'))
        data['size'] = int(round(data['size'], 0))
        
        raw = node.find('span', class_='c-pa-cprice').contents[0]
        data['price'] = int(''.join(char for char in raw if char.isdigit()))

        data['city'] = node.find('div', class_='c-pa-city').contents[0]
        data['zip_code'] = (node.find('div', class_='h-fi-pulse')
                                .get('data-codepostal'))

        data['type'] = node.find('a', class_='c-pa-link').contents[0]
        data['project'] = self.project
        return data

    def get_content(self, url):
        
        self.session.get(url)
        time.sleep(4)

        if self.session.can_find_class("content_result"):
            return self.session.get_content()
        return ""

    def build_url(self, project=None, types=None, cp=75):

        if not project:
            project = seloger.ACHAT

        assert isinstance(project, int)
        assert project in seloger.PROJECTS

        if not types:
            types = (seloger.APPARTEMENT, seloger.MAISON)
        elif isinstance(types, int):
            types = (types,)  # converting to tuple for formalization
        for t in types:
            assert t in seloger.TYPES

        self.project = project
        self.types = types

        url = seloger.ROOT_URL

        if len(types) > 1:
            types = ','.join(map(str, sorted(types)))

        url += "{}={}".format(seloger.PROJECT_URL, project)
        url += "&{}={}".format(seloger.TYPES_URL, types)
        url += "&{}={}".format(seloger.CODE_POSTAL, cp)


        url += "&naturebien=1,2,4&pxMax=350000&surfaceMin=30&sort=d_dt_crea"
        return url


    def delete_table(self):
        with SQLite(self.db) as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE name='seloger';
            """)
            if cursor.fetchall():
                cursor.execute("""DROP TABLE seloger;""")
        return True


    def create_table(self):
        with SQLite(self.db) as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE name='seloger';
            """)
            if not cursor.fetchall():
                cursor.execute("""
                    CREATE TABLE seloger (
                        'id' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        'date' DATE,
                        'project' TEXT,
                        'type' TEXT,
                        'city' TEXT,
                        'zip_code' TEXT,
                        'size' TEXT,
                        'price' INTEGER,
                        'rooms' INTEGER,
                        'bedrooms' INTEGER,
                        'URL' TEXT,
                        'date_publication' DATE
                    );
                """)
        return True
