from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time

# Create Chrome options
chrome_options = webdriver.ChromeOptions()

# Add headless option for running on a server
chrome_options.add_argument('--headless')

chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Create a Selenium webdriver with the specified options
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
# URLs of the pages containing news articles
urls = {
    'eurusd': 'https://www.fxstreet.com/currencies/eurusd'
    # 'gbpusd': 'https://www.fxstreet.com/currencies/gbpusd',
    # 'usdjby': 'https://www.fxstreet.com/currencies/usdjpy',
    # 'audusd': 'https://www.fxstreet.com/currencies/audusd',
    # 'usdcad': 'https://www.fxstreet.com/currencies/usdcad',
    # 'oil': 'https://www.fxstreet.com/markets/commodities/energy/oil',
    # 'gold': 'https://www.fxstreet.com/markets/commodities/metals/gold'
}

# Initialize a dictionary to store data for each URL
all_data = {}

for url_name, url in urls.items():  # Loop through the dictionary with items()
    driver.get(url)
    time.sleep(20)

    # Wait for the page to load (you may need to adjust the wait time)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.fxs_flex_col')))

    # Get the page source after waiting
    page_source = driver.page_source

    # Parse the HTML content of the page
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all news article containers
    article_containers = soup.find_all('div', class_='fxs_col editorialhighlight editorialhighlight_no_image')

    # Initialize a list to store news data for this URL
    url_data = []

    # Loop through the article containers and extract data
    for article_container in article_containers:
        data = {}

        # Extract the headline
        headline = article_container.find('h2', class_='fxs_headline_from_medium_to_large').text.strip()
        data['headline'] = headline

        # Extract the article content
        article_content = article_container.find('div', class_='fxs_entryPlain_txt').find('p').text.strip()
        data['article_content'] = article_content

        # Extract the URL
        article_url = article_container.find('script', type='application/ld+json')
        if article_url:
            article_url = json.loads(article_url.text)['url']
            data['article_url'] = article_url

        url_data.append(data)

    # Find the second news element by its class
    second_container = soup.find('div', class_='fxs_widget_chart')
    time.sleep(5)

    if second_container:
        # Extract the chart URL
        chart = second_container.find('a', class_='fxs_btn')

        if chart:
            chart_url = chart['href']
        else:
            chart_url = None

    else:
        chart_url = None

    # Find the third news element by its class
    third_container = soup.find('div', class_='fxs_col editorialhighlight editorialhighlight_fundamental')

    if third_container:
        # Find the paragraph elements within the article content
        paragraphs = third_container.find_all('p')

        # Initialize a variable to store the extracted text
        article_text = ""

        # Loop through the paragraphs and concatenate their text
        for paragraph in paragraphs:
            article_text += paragraph.text.strip() 
    else:
        article_text = None

    # Find the <aside> element with class 'fxs_entriesList'
    aside_element = soup.find('aside', class_='fxs_entriesList')

    # Initialize a list to store the latest news links
    latest_news_links = []

    # Check if the <aside> element is found
    if aside_element:
        # Find the <ol> element within the <aside> element
        ol_element = aside_element.find('ol')

        # Check if the <ol> element is found
        if ol_element:
            # Loop through the <li> elements within the <ol> and extract the links and titles
            li_elements = ol_element.find_all('li')
            for li_element in li_elements:
                link_element = li_element.find('a')
                if link_element:
                    link = link_element['href']
                    title = link_element.text.strip()

                    latest_news_links.append({
                        'title': title,
                        'link': link
                    })

    # Store the data for this URL in the dictionary
    all_data[url_name] = {
        "data": url_data,
        "chart_url": chart_url,
        "article_text": article_text,
        "latest_news_links": latest_news_links  # Add the latest news links to the data
    }

# Close the webdriver
driver.quit()

# Save the data to a JSON file with one section for each URL
with open('all_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_data, json_file, ensure_ascii=False, indent=4)

print("Data saved to all_data.json")
