import requests 
from bs4 import BeautifulSoup
import random
import pandas as pd

# scrap targe movie information: name, storyline, release date, rating, tag, runtime, post    
def fetch_element_text(soup, selector, property_name=None):
    """Fetch text from a specified element or property."""
    if property_name:
        element = soup.find(selector, property=property_name)
    else:
        element = soup.find(selector)
    
    return element.text.strip() if element else ''

def fetch_multiple_elements_text(soup, selector, property_name=None):
    """Fetch text from multiple specified elements or properties."""
    elements = soup.find_all(selector, property=property_name)
    return ' '.join(element.text.strip() for element in elements)

def scrap_movie_information(url, headers, proxies):
    # Anti-anti-crawling settings
    response = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(response.text, features='html.parser')

    # Collect movie information
    movie_info = {
        'name': fetch_element_text(soup, 'span', 'v:itemreviewed'),
        'storyline': fetch_element_text(soup, 'span', 'v:summary').replace(' ', ''),
        'release date': fetch_multiple_elements_text(soup, 'span', 'v:initialReleaseDate'),
        'rate score': fetch_element_text(soup, 'strong', 'll rating_num'),
        'rate people sum': fetch_element_text(soup, 'a', 'rating_people'),
        'tag': fetch_multiple_elements_text(soup, 'span', 'v:genre'),
        'run time': fetch_element_text(soup, 'span', 'v:runtime')
    }

    # Rating percentages from 1 to 5 stars
    rate_per = {}
    for i in range(5, 0, -1):
        rate_star_num = fetch_element_text(soup, 'span', f'stars{i} starstop')
        rate_star_num_per = fetch_element_text(soup, 'span', 'rating_per')
        if rate_star_num:  # Only add if the star number exists
            rate_per[rate_star_num] = rate_star_num_per

    # Combine all information
    movie_info.update(rate_per)

    # Create DataFrame
    df = pd.DataFrame.from_records([movie_info])  # Create DataFrame from single record
    print(df)

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

url = 'https://movie.douban.com/subject/36934908/'

scrap_movie_information(url, headers, proxies)

