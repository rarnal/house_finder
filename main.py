from services.seloger import ServiceSeloger
from bs4 import BeautifulSoup

if __name__ == "__main__":
    sv = ServiceSeloger()
    content = sv.refresh_database(cp=[78, 91, 77, 94, 44, 69])

    
