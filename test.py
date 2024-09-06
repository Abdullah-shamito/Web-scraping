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
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")

# Create a Selenium webdriver with the specified options
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

urls = {
    'MSFT': 'https://www.google.com/finance/quote/MSFT:NASDAQ'
}

all_data = {}

for url_name, url in urls.items():
    driver.get(url)
    time.sleep(20)

    try:
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.e1AOyf')))
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        url_data = {'statistics': [], 'financials': {}}

        data_containers = soup.find_all('div', class_='e1AOyf')
        for data_container in data_containers:
            statistics = {}
            p6k39c_divs = data_container.find_all('div', class_='P6K39c')
            if len(p6k39c_divs) >= 7:
                statistics['previous_close'] = p6k39c_divs[0].text.strip()
                statistics['day_range'] = p6k39c_divs[1].text.strip()
                statistics['year_range'] = p6k39c_divs[2].text.strip()
                statistics['market_cap'] = p6k39c_divs[3].text.strip()
                statistics['avg_volume'] = p6k39c_divs[4].text.strip()
                statistics['pe_ratio'] = p6k39c_divs[5].text.strip()
                statistics['dividend_yield'] = p6k39c_divs[6].text.strip()
                url_data['statistics'].append(statistics)

        tab_ids = ['option-0', 'option-1', 'option-2', 'option-3', 'option-4']

        for tab_id in tab_ids:
            tab = driver.find_element(By.ID, tab_id)
            tab.click()
            time.sleep(2)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            financials = {}
            financials_container = soup.find('table', class_='slpEwd')

            if financials_container:
                rows = financials_container.find_all('tr', class_='roXhBd')
                for row in rows[1:]:
                    label_element = row.find('div', class_='rsPbEe')
                    value_element_1 = row.find('td', class_='QXDnM')
                    value_element_2 = row.find('td', class_='gEUVJe')
                    
                    if label_element and value_element_1 and value_element_2:
                        label = label_element.text.strip()
                        value1 = value_element_1.text.strip()
                        value2 = value_element_2.text.strip()
                        combined_values = f"{value1}, {value2}".strip(", ")
                        if label == "Revenue":
                            financials['revenue'] = combined_values
                        if label == "Operating expense":
                            financials['operating_expenses'] = combined_values
                        elif label == "Net profit margin":
                            financials['net_profit_margin'] = combined_values
                        elif label == "Earnings per share":
                            financials['earnings_per_share'] = combined_values
                        elif label == "EBITDA":
                            financials['ebitda'] = combined_values
                        elif label == "Effective tax rate":
                            financials['effective_tax_rate'] = combined_values

            url_data['financials'][tab_id] = financials

        all_data[url_name] = url_data

    except TimeoutException:
        print(f"Timed out waiting for the element to appear for URL {url}. Continuing with next URL...")

driver.quit()

for name, data in all_data.items():
    filename = f"{name}.json"
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}")
