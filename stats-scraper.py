from curl_cffi import requests
import json
import os

folder_path = 'data'

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9,ur;q=0.8,mt;q=0.7,fr;q=0.6',
    'cache-control': 'no-cache',
    'content-encoding': 'gzip, deflate, br',
    'content-type': 'application/json',
    # 'cookie': '_fbp=fb.1.1714578410684.1927166007; _gcl_au=1.1.624693773.1714578411; _gid=GA1.2.400907382.1714578412; _hjSessionUser_807065=eyJpZCI6ImU4N2ZkNTA2LTZiOTktNWJjOS05ZjVhLTRhNTE3NjYyZGFiMSIsImNyZWF0ZWQiOjE3MTQ1Nzg0MTQ5NjAsImV4aXN0aW5nIjp0cnVlfQ==; __adroll_fpc=c6a73722a8174510cca2c7b170d126de-1714578420351; zt_Ses=4fxcc0y2zqgz0gp0djtx50tr; zt_Fl=ZuluTrade; JSESSIONID=E3E96B35A73E48C52F507AE7F4E558C8; _ga=GA1.2.933866918.1714578411; _gat_UA-1958810-11=1; _gat_UA-1958810-1=1; MgidSensorNVis=10; MgidSensorHref=https://www.zulutrade.com/traders/list/82236; _hjSession_807065=eyJpZCI6Ijc3NGEzYzI3LWMxYTktNGRmNi1hMGJlLWQ1NTc5NWQyYjM2MiIsImMiOjE3MTQ2NjQ0Nzg2ODgsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; __ar_v4=Q5GVRMJ6JVFRZDWVZ2S32G%3A20240431%3A6%7CWTH7PDX23RBFLDCDHMXOU2%3A20240431%3A6%7CEVSHUVSNC5HHXGH7UWTIGW%3A20240431%3A6; _ga_CNT6FMR9VW=GS1.1.1714664459.2.1.1714664500.19.0.0',
    'origin': 'https://www.zulutrade.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.zulutrade.com/traders/list/82236',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}


def get_traders(page=0):
    all_traders = []
    pages_crawled = 0  # Counter for pages crawled
    while True:
        if pages_crawled == 10:
            break  # Break the loop after 10 pages
        print(f"[*] crawling page: {page}")
        json_data = {
            'accessingFlavorId': 1,
            'backendid': 6,
            'bringDetailedChart': True,
            'flavor': 'global',
            'page': page,
            'size': 100,
            'sortAsc': False,
            'sortBy': 'uninterruptedLiveFollowerProfit',
            'timeFrame': 365,
        }

        response = requests.post(
            'https://www.zulutrade.com/zulutrade-gateway/v2/api/providers/performance/search',
            headers=headers,
            json=json_data, impersonate='chrome120'
        )

        jd = response.json()
        results = jd.get('result')
        for result in results:
            trader = result.get("trader")
            trader_id = trader.get("providerId")
            all_traders.append(get_stats(trader_id))
        if len(results) < 1:
            break
        else:
            page += 1
            pages_crawled += 1  # Increment the counter

    return all_traders

def seconds_to_hours(seconds):
    hours = seconds / 3600
    if hours < 24:
        return f"{round(hours)} Hours"
    days = hours / 24
    return f"{round(days)} Days"

def get_stats(trader_id, stats_format="365"):
    print(f"\t[+] scraping: {trader_id}")
    params = {
        'accessingFlavorId': '1',
        'flavor': 'global',
    }

    response = requests.get(
        f'https://www.zulutrade.com/zulutrade-gateway/v2/api/providers/{trader_id}/thi/init',
        params=params,
        headers=headers, impersonate='chrome120'
    )
    jd = response.json()
    trader = jd.get("trader")
    stats = trader.get("stats")
    profile = stats.get("profile")
    stats_frame = stats.get("timeframeStats").get(stats_format)

    return {
        "traderId": trader_id,
        "traderName": profile.get("name"),
        "profit": stats_frame.get("totalProfitMoney"),
        "trades": stats_frame.get("trades"),
        "maxOpenTrades": stats_frame.get("maxOpenTrades"),
        "winTrades": stats_frame.get("winTrades"),
        "winTradesCount": stats_frame.get("winTradesCount"),
        "recommendedMin": stats_frame.get(
            "recommendedGlobalMinAmountDollarValue"
        ),
        "overallDrawDownMoney": stats_frame.get("overallDrawDownMoney"),
        "profitPercentage": round(stats_frame.get("profitPercentage"), 2),
        "avgTradeTime": f'{seconds_to_hours(stats_frame.get("avgTradeSeconds"))}',
    }

output_json = get_traders()
with open(f"{folder_path}/stats.json", "w", encoding="utf-8") as f:
    json.dump(output_json, f, indent=3)