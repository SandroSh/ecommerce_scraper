import requests
from bs4 import BeautifulSoup
from src.data.models import  Product
from src.data.database import SessionLocal
import time

class EEScraper:
    BASE_URL = "https://ee.ge/mobiluri-telefonebi-da-aqsesuarebi/mobiluri-telefonebi"

    def __init__(self, max_products=0, sleep=1.0):
        self.session = SessionLocal()
        self.max_products = max_products
        self.sleep = sleep

    def get_all_listing_pages(self):
        res = requests.get(self.BASE_URL)
        soup = BeautifulSoup(res.content, "html.parser")

        page_links = soup.select("ul.pagination li.page-item a.page-link")
        urls = set()

        for a in page_links:
            href = a.get("href")
            if href and "page=" in href:
                full_url = href if href.startswith("http") else f"https://ee.ge{href}"
                urls.add(full_url)

        urls.add(self.BASE_URL)
        return sorted(urls)

    def get_product_links(self, page_url):
        res = requests.get(page_url)
        soup = BeautifulSoup(res.content, "html.parser")

        links = []
        for a in soup.select(".product-list .thumb-wrap a"):
            href = a.get("href")
            if href:
                full_url = f"https://ee.ge{href}" if not href.startswith("http") else href
                links.append(full_url)
        return links



