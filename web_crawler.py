import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException 
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

import traceback
import os

def get_soup(url, headers, proxies):
    """Fetch the content of the URL and return a BeautifulSoup object."""
    response = requests.get(url, headers=headers, proxies=proxies)
    return BeautifulSoup(response.text, features='html.parser')

    # set Chrome options
def set_chrome_options(user_agents, proxies, setting=True):
    if setting:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')
        chrome_options.add_argument(f'--proxy-server={proxies}')
        return webdriver.Chrome(options = chrome_options)
    else:
        return webdriver.Chrome()

def extract_movies(movies, setting = 'soup'):
    """Extract movie names and links from a list of movie elements."""
    if setting == 'soup':
        return [
            {
                'name': movie.find('a').text.strip().replace('\n', '').replace(' ', ''),
                'link': movie.find('a')['href']
            }
            for movie in movies if movie.find('a')
        ]
    elif setting == 'selenium':
        movie_list = []
        seen_links = set()
        i = 1
        for movie in movies:
            # check if the movie element is visible
            if movie.is_displayed():
                try:
                    # //*[@id="content"]/div/div[1]/div[6]/div[1]/div/div/div[1]/span[1]/a
                    # //*[@id="content"]/div/div[1]/div[6]/div[2]/div/div/div[1]/span[1]/a
                    # //*[@id="content"]/div/div[1]/div[6]/div[40]/div/div/div[1]/span[1]/a
                    print(movie.find_element(By.XPATH, f'//*[@id="content"]/div/div[1]/div[6]/div[{i}]/div/div/div[1]/span[1]/a').text, movie.find_element(By.XPATH, f'//*[@id="content"]/div/div[1]/div[6]/div[{i}]/div/div/div[1]/span[1]/a').get_attribute('href'))
                    name = movie.find_element(By.XPATH, f'//*[@id="content"]/div/div[1]/div[6]/div[{i}]/div/div/div[1]/span[1]/a').text.replace('\n', '').replace(' ', '').strip()
                    link = movie.find_element(By.XPATH, f'//*[@id="content"]/div/div[1]/div[6]/div[{i}]/div/div/div[1]/span[1]/a').get_attribute('href')
                    # Only append if we haven't seen this link before
                    if name and link and (link not in seen_links):
                        seen_links.add(link)
                        movie_list.append({'name': name, 'link': link})
                    i += 1
                except Exception as e:
                    print(f"Error extracting movie: {e}")
            
        df = pd.DataFrame(movie_list)
        return df


def scroll_down(driver, pause_time, max_scroll_attempts):
    # Track the last scroll height to detect if scrolling reaches the bottom
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    scroll_attempts = 0
    while scroll_attempts < max_scroll_attempts:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new items to load
        time.sleep(pause_time)
        
        # Get the new scroll height and compare with last height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            # If the height hasn't changed, assume we've reached the end of the page
            print(f"Reached the end of the page after {scroll_attempts} scrolls.")
            break
        
        # Log the current scroll height for debugging
        print(f"Scroll attempt {scroll_attempts + 1}, new height: {new_height}")
        
        last_height = new_height
        scroll_attempts += 1
    
def show_all_db(db_name):
    conn = sqlite3.connect(f'{db_name}.db')
    c = conn.cursor()
    c.execute(f"""
        SELECT * FROM {db_name} 
    """)
    items = c.fetchall()
    for item in items:
        print(item)
    conn.commit()
    conn.close()

def delete_db(db_name):
    try:
        os.remove(f'{db_name}.db')
        print(f"Database '{db_name}.db'' deleted successfully.")
    except FileNotFoundError:
        print(f"Database '{db_name}.db'' not found.")
    except Exception as e:
        print(f"Error occurred while deleting database: {e}")

def delete_table(db_name, table_name):
    try:
        conn = sqlite3.connect(f'{db_name}.db')
        c = conn.cursor()
        c.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.commit()
        print(f"Table '{table_name}' deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error occurred while deleting table: {e}")
    finally:
        conn.close()

def save_link_to_db(df, db_name, table_name, name_title):
    # connect to database
    conn = sqlite3.connect(f'{db_name}.db')
    c = conn.cursor()
    # create table
    # need to write different SQL for different table structure
    c.execute("""
        CREATE TABLE IF NOT EXISTS new_movies(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXTE,
              link TEXT)
    """)
    # save data to db
    for _, row in df.iterrows():
        c.execute(f"INSERT INTO {table_name} ({name_title}, link) VALUES (?, ?)", (row['name'], row['link']))
    conn.commit()
    conn.close()

def crawl_new_movies(url, headers, proxies):
    # anti-anti-crawling setting
    soup = get_soup(url, headers, proxies)

    # get all new movies' names & links
    movies = soup.find_all('div', class_ = 'pl2')

    movie_list = extract_movies(movies)
    df = pd.DataFrame(movie_list)
    print(df)
    save_link_to_db(df, db_name = 'link', table_name = 'hot_movies', name_title = 'movie_name')
    # return df

def crawl_top_movies(url, headers, proxies):
    # anti-anti-crawling setting
    soup = get_soup(url, headers, proxies)

    #get all top movies' names & links
    movies = soup.find_all('li', class_='clearfix')
    movie_list = extract_movies(movies)
    df = pd.DataFrame(movie_list)
    print(df)
    save_link_to_db(df, db_name = 'link', table_name = 'hot_movies', name_title = 'movie_name')
    # return df

def crawl_movie_types(url, headers, proxies):
    # anti-anti-crawling setting
    soup = get_soup(url, headers, proxies)

    # get all movie types and revelent links
    types = soup.find('div', class_='types').find_all('span')
    type_list = extract_movies(types)
    df = pd.DataFrame(type_list)
    save_link_to_db(df, db_name = 'link', table_name = 'movie_types', name_title = 'type_name')
    # return df

def crawl_type_movies(url, user_agents, proxies):
    driver = set_chrome_options(user_agents, proxies, setting=False)
    driver.get(url)
     # Scroll down to load more content
    scroll_down(driver, pause_time=10, max_scroll_attempts=2)
    
    try:
        # Wait for the movies to be visible after scrolling
        movies = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'movie-name-text'))
        )
        print(f"Found {len(movies)} movies")
    except TimeoutException:
        print("Timed out waiting for page to load")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()  # 打印完整的错误堆栈
    print("starting extracting data...")
    # Extract movies
    movie_list = extract_movies(movies, setting='selenium')
    df = pd.DataFrame(movie_list)
    print(df)
    save_link_to_db(df, db_name = 'link', table_name = 'type_movies', name_title = 'movie_name')
    # return df

def crawl_top250(url, headers, proxies):
    # anti-anti-crawling setting
    soup = get_soup(url, headers, proxies)

    # crawl top250 page link
    top250 = soup.find('div', class_ = 'douban-top250-hd').find('h2')
    link = top250.find('a')['href']
    top250.find('span').decompose()
    title = top250.get_text().replace('\n', '').replace(' ','').strip()
    df = pd.DataFrame([{'type':title, 'link': link}])
    print(df)
    save_link_to_db(df, db_name = 'link', table_name = 'top250', name_title = 'top250')
    # return df

def crawl_top250_movies(url, headers, proxies):
    #get all top movies' names & links
    movie_list = []
    for n in range(10):
        start_num = n*25
        page_url = f'?start={start_num}'
        # anti-anti-crawling setting
        soup = get_soup(url+page_url, headers, proxies)
        
        movies =  soup.find_all('div', class_='hd')
        for movie in movies:
            name_elements = movie.find_all('span', class_ = 'title')
            name = ' '.join(element.text.strip() for element in name_elements)
            link = movie.find('a')['href']
            item = {'name': name,
                    'link': link}
            movie_list.append(item)
    df = pd.DataFrame(movie_list)
    print(df)
    save_link_to_db(df, db_name = 'link', table_name = 'top250_movies', name_title = 'movie_name')
    # return df

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

# url = 'https://movie.douban.com/chart'

# new_movies_df = crawl_new_movies(url, headers, proxies)
# print(new_movies_df)

# top_movies_df = crawl_top_movies(url, headers, proxies)
# print(top_movies_df)

# movie_types_df = crawl_movie_types(url, headers, proxies)
# print(movie_types_df)

# url = 'https://movie.douban.com/typerank?type_name=%E5%89%A7%E6%83%85&type=11&interval_id=100:90&action='
# type_movies_df = crawl_type_movies(url, user_agents, proxies)
# print(type_movies_df)

# top250_df = crawl_top250(url, headers, proxies)
# print(top250_df)

# url = 'https://movie.douban.com/top250'
# top250_movies_df = crawl_top250_movies(url, headers, proxies)
# print(top250_movies_df)

