import requests 
from bs4 import BeautifulSoup
import random

# against anti-scraping setting
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
]
headers = {
    'User-Agent': random.choice(user_agents)
}

# use proxes
proxies = {
    'http': 'http://47.121.183.107:8443'
    # 'https': 'https://47.121.183.107:8443'
}

top250_url = 'https://movie.douban.com/top250'

top250_response = requests.get(top250_url, headers = headers, proxies = proxies)

top250_soup = BeautifulSoup(top250_response.text, 'html.parser')

top250_titles_all = top250_soup.find_all('span', class_=['title', 'other'])
top250_titles = [title.text.strip().replace('\xa0','') for title in top250_titles_all]

print(top250_titles)

