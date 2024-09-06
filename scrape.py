import csv
import re

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def scrape():
    with sync_playwright() as p:
        print("[+] Opening Browser")
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()

        page.goto('https://www.adss.com/en/analysis/economic-calendar/', timeout=50000)
        accept_button = page.wait_for_selector('[data-testid="uc-accept-all-button"]')
        accept_button.click()

        page.wait_for_selector('[class="EventTile__wrapper__iAmCe "]')
        soup = BeautifulSoup(page.content(), 'lxml')
        main_divs = soup.findAll('div', 'EventTile__wrapper__iAmCe')
        print(len(main_divs))
        for div in main_divs:
            impact = country = event_name = event_time = Actual = previous = Forecast = ''
            top_panel = div.find('div', 'EventTile__topPanel__u9R6F')
            if top_panel:
                imp_span = top_panel.find('span')
                if imp_span:
                    impact = imp_span.text.strip()
                con_img = top_panel.find('img')
                if con_img:
                    country = con_img.get('alt')
            content_panel = div.find('div', 'EventTile__tileContent__Jdh9N')
            if content_panel:
                ev_nm = content_panel.find('div', 'EventTile__eventName__OBN72')
                if ev_nm:
                    event_name = ev_nm.text.strip()
                ev_time = content_panel.find('div', re.compile(r'EventTile__eventTime__\w+'))
                if ev_time:
                    time_div = ev_time.find('div', attrs={})
                    if ":" in time_div.text:
                        event_time = time_div.text.strip()
                ev_detail = content_panel.find('div', re.compile('EventTile__eventDetails__\w+'))
                if ev_detail:

                    detail_items = ev_detail.findAll('div', re.compile('EventTile__detailItem__\w+'))
                    for item in detail_items:
                        if "Previous" in str(item.find('div', re.compile('EventTile__detailItemName__\w+'))):
                            previous = item.find('div', re.compile('EventTile__detailItemValue__\w+')).text.strip()
                        if "Forecast" in str(item.find('div', re.compile('EventTile__detailItemName__\w+'))):
                            Forecast = item.find('div', re.compile('EventTile__detailItemValue__\w+')).text.strip()
                        if "Actual" in str(item.find('div', re.compile('EventTile__detailItemName__\w+'))):
                            Actual = item.find('div', re.compile('EventTile__detailItemValue__\w+')).text.strip()
                        # print(previous,Forecast,Actu`al)
            out = [event_name, impact, country, event_time, Actual, previous, Forecast]
            wr.writerow(out)
        browser.close()


with open('output.csv', 'w', encoding='utf-8', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(['Event_Name', 'Impact', 'Country', 'Event_Time', 'Actual', 'Previous', 'Forecast'])
    scrape()
