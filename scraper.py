from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.action_chains import ActionChains

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# This initializes the driver once and can be reused for every call to get_data
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


def accept_cookies(driver):
    time.sleep(10)
    try:
        
        driver.find_element(By.XPATH, '//form[@style="display:inline;"]//button[@aria-label="Accept all"]').click()
        # Save the screenshot after clicking the 'Accept all' button
        
        
        time.sleep(5)
    except Exception as e:
        print(e)
        print("Failed to click on 'Accept all' button. Proceeding...")


def get_data(ticker, exchange):
    url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"

    driver.get(url)
    s = driver.page_source
    # with open("s.html", "w") as f:
    #     f.write(s)
    # Accept cookies to handle the consent page.
    accept_cookies(driver)
    wait = WebDriverWait(driver, 60)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.e1AOyf')))
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extracting statistics data
    statistics = {}
    data_containers = soup.find_all('div', class_='e1AOyf')
    for data_container in data_containers:
        p6k39c_divs = data_container.find_all('div', class_='P6K39c')
        if len(p6k39c_divs) >= 7:
            statistics['previous_close'] = p6k39c_divs[0].text.strip()
            statistics['day_range'] = p6k39c_divs[1].text.strip()
            statistics['year_range'] = p6k39c_divs[2].text.strip()
            statistics['market_cap'] = p6k39c_divs[3].text.strip()
            statistics['avg_volume'] = p6k39c_divs[4].text.strip()
            statistics['pe_ratio'] = p6k39c_divs[5].text.strip()
            statistics['dividend_yield'] = p6k39c_divs[6].text.strip()

    financials_array = []  # Create an array to store financial data
    tab_ids = ['option-0', 'option-1', 'option-2', 'option-3', 'option-4']
    for tab_id in tab_ids:
        financials = {}
        tab = driver.find_element(By.ID, tab_id)
        tab.click()
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
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

                    if label in ["Revenue", "Operating expense", "Net profit margin",
                                 "Earnings per share", "EBITDA", "Effective tax rate"]:
                        financials[label.lower().replace(" ", "_").replace("/", "_")] = combined_values

        # Extract the date from the tab using class 'VfPpkd-vQzf8d'
        date_element = tab.find_element(By.CLASS_NAME, 'VfPpkd-vQzf8d')
        date = date_element.text.strip()

        # Append the date to the financials dictionary
        financials['date'] = date

        financials_array.append(financials)  # Append financials to the array

    return {"ticker": ticker, "statistics": statistics, "financials": financials_array}


if __name__ == '__main__':
    # Example usage:
    result = get_data("AAPL", "NASDAQ")
    print(result)
    driver.quit()  # Close the WebDriver when done
