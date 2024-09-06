from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# This initializes the driver once and can be reused for every call to get_data
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_data(ticker):
    url = f"https://www.energyexch.com/market/{ticker}"
    driver.get(url)
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.flexposts__item.flexposts__story.flexposts__story--none.flexposts__story--large.story.large')))
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extracting stories data
    stories = {}
    data_containers = soup.find_all('li', class_='flexposts__item flexposts__story flexposts__story--none flexposts__story--large story large')
    for index, data_container in enumerate(data_containers):
        story_title = data_container.find('a').get_text(strip=True)
        story_link = data_container.find('a')['href']
        stories[index] = {'title': story_title, 'link': story_link}

    return stories

# Example usage
ticker = 'natgasusd'
print(get_data(ticker))
