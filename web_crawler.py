from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://movie.douban.com/chart'

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
]
headers = {
    'User-Agent': random.choice(user_agents)
}
proxies = {
    'http': 'http://47.121.183.107:8443'
    # 'https': 'https://47.121.183.107:8443'
}

def crawl_new_movies(url, headers, proxies):
    # anti-anti-crawling setting
    response = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(response.text, features = 'html.parser')

    # get all new movies' names & links
    movies = soup.find_all('div', class_ = 'pl2')

    movie_list = []
    for movie in movies:
        element = movie.find('a')
        name = element.get_text()
        cleaned_name = name.replace('\n', '').replace(' ','').strip()
        link = element['href']
        movie_item = {
            'name': cleaned_name,
            'link': link
        }
        movie_list.append(movie_item)
        
    df = pd.DataFrame(movie_list)
    return df

def crawl_top_movies(url, headers, proxies):
    # anti-anti-crawling setting
    response = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(response.text, features = 'html.parser')

    #get all top movies' names & links
    movies = soup.find_all('li', class_='clearfix')
    movie_list = []
    for movie in movies:
        element = movie.find('a')
        name = element.get_text()
        cleaned_name = name.replace('\n', '').replace(' ','')
        link = element['href']
        movie_item = {
            'name': cleaned_name,
            'link': link
        }
        movie_list.append(movie_item)
    df = pd.DataFrame(movie_list)
    return df

# new_movies_df = crawl_new_movies(url, headers, proxies)
# print(new_movies_df)

top_movies_df = crawl_top_movies(url, headers, proxies)
print(top_movies_df)

# # selenium
# # set Chrome options
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument(f'user-agent = {random.choice(user_agents)}')
# chrome_options.add_argument(f'--proxy-server = {proxies}')
# driver = webdriver.Chrome(options = chrome_options)

# driver.get(url)

# movies = driver.find_elements(By.CLASS_NAME, "pl2")
# i = 1
# for movie in movies:
#     name  = movie.find_element(By.XPATH, f'//*[@id="content"]/div/div[1]/div/div/table[{i}]/tbody/tr/td[2]/div/a').text.strip()
#     try:
#         other_name = movie.find_element(By.XPATH, f'//*[@id="content"]/div/div[1]/div/div/table[{i}]/tbody/tr/td[2]/div/a/span').text.strip()
#     except:
#         other_name = ' '
#     link = movie.find_element(By.XPATH, f'//*[@id="content"]/div/div[1]/div/div/table[{i}]/tbody/tr/td[2]/div/a').get_attribute('href')

#     print(name,other_name,link)
#     i += 1
    
# driver.quit()
