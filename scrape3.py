import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta


def setup_chrome(headless=True):
    """Setup and return a chrome webdriver instance."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    if headless:
        chrome_options.add_argument('--headless')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def fetch_news_data(driver):
    """Fetch and return news data from the current page."""
    news_data = []
    
    # Locate all news articles
    news_articles = driver.find_elements(By.CSS_SELECTOR, '.News__articleWrapper__X8z8u')
    
    for article in news_articles:
        date_str = article.find_element(By.CSS_SELECTOR, '.News__date__YBXJ0').text
        # Parse and reformat date
        date_obj = datetime.strptime(date_str, '%d %b %Y %H:%M')
        date = date_obj.strftime('%Y-%m-%dT%H:%M:00Z')
        headline = article.find_element(By.CSS_SELECTOR, '.News__articleHeadline__rdWH4').text
        body = article.find_element(By.CSS_SELECTOR, '.News__articleBody__I4KCh').text
        
        news_data.append({
            'date': date,
            'headline': headline,
            'body': body
        })

    return news_data


def fetch_events_data(driver, url):
    """Fetch and return event data from the specified URL."""
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.EventsCarousel__eventTiles__nvPqr')))
    
    events = []
    event_buttons = driver.find_elements(By.CSS_SELECTOR, 'div.EventTile__wrapper__iAmCe')

    for btn in event_buttons:
        try:
            driver.execute_script("arguments[0].click();", btn)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.EventInfo__wrapper__Gkjqn')))

            time.sleep(2)
            current_date = datetime.now().strftime('%B %d, %Y')

            time_str = btn.find_element(By.CSS_SELECTOR, 'div.EventTile__eventTime__mEKPW div').text
            hour, minute = map(int, time_str.split(':'))

            event_datetime = datetime.strptime(current_date, '%B %d, %Y').replace(hour=hour, minute=minute)
            # event_datetime = event_datetime + timedelta(hours=3)
            timestamp = event_datetime.isoformat() + 'Z'
            

            event_data = {
                'impact_level': btn.find_element(By.CSS_SELECTOR, 'div.EventTile__eventImpactLevel__j_RbZ span').text,
                'country': btn.find_element(By.CSS_SELECTOR, 'div.EventTile__eventCountry__cU_fG div').text,
                'title': btn.find_element(By.CSS_SELECTOR, 'div.EventTile__eventName__OBN72').text,
                'timestamp': timestamp,
                'forecast': btn.find_element(By.CSS_SELECTOR, 'div.EventTile__detailItem__qBuQr:nth-of-type(2) .EventTile__detailItemValue__O5hYn').text,
                'actual': btn.find_element(By.CSS_SELECTOR, 'div.EventTile__detailItem__qBuQr:nth-of-type(3) .EventTile__detailItemValue__O5hYn').text,
                'description': driver.find_element(By.CSS_SELECTOR, 'div.EventInfo__longDescription__UXBAS').text,
                'affected_assets': [asset.text for asset in driver.find_elements(By.CSS_SELECTOR, 'div.EventInfo__affectedAsset__iQlBc span')],
                'news': fetch_news_data(driver)
            }

            events.append(event_data)
            
        except:
            print("Timeout while waiting for the element. Continuing with the next button.")

    return events


def main():
    """Main function to fetch event data and save to a JSON file."""
    driver = setup_chrome(headless=False)
    url = 'https://www.adss.com/en/analysis/economic-calendar/'

    print("Fetching events data...")
    events = fetch_events_data(driver, url)

    if events:
        with open('events.json', 'w', encoding='utf-8') as json_file:
            json.dump(events, json_file, ensure_ascii=False, indent=4)
        print('Event data has been scraped and saved to events.json')
    else:
        print('No event data found!')

    driver.quit()


if __name__ == '__main__':
    main()
