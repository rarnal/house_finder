from services.seloger import ServiceSeloger
from bs4 import BeautifulSoup


def test_service_seloger_build_url():
    sv = ServiceSeloger()
    url = sv.build_url(project=2, types=(2, 1))
    assert url == "https://www.seloger.com/list.htm?idtt=2&idtypebien=1,2"


def test_service_seloger_content_getter():
    url = "https://www.seloger.com/list.htm?idtt=2&idtypebien=1,2"
    sv = ServiceSeloger()
    url = sv.get_content(url)
    assert url.status_code == 200
