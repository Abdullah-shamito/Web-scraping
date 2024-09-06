import json
import os
import random
import time
from datetime import datetime, timezone, timedelta

from curl_cffi import requests

folder_path = 'data'

if not os.path.exists(folder_path):
    os.makedirs(folder_path)


def generate_datetime_one_year_back():
    current_datetime = datetime.now(timezone.utc)
    one_year_ago = current_datetime - timedelta(days=365)

    return one_year_ago.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


cookies = {
    'eToroLocale': 'en-gb',
    '__cfruid': '701ca3b053347f68afe71aa5c6508ea79664a7a2-1688533705',
    '_gcl_au': '1.1.230344400.1688533722',
    '_scid': '66d7c34d-d672-46de-8fd6-33661f7ffd79',
    '__adal_ca': 'so%3Ddirect%26me%3Dnone%26ca%3Ddirect%26co%3D%28not%2520set%29%26ke%3D%28not%2520set%29',
    '__adal_cw': '1688533725433',
    '_gid': 'GA1.2.1867234857.1688533726',
    '_sctr': '1%7C1688497200000',
    '__cflb': '0roHE7fJv84VGKKkmohyeKBNpLLZvPHCS98PqRYWmWEYk4kJRQDero1x8zohocQ17FT7xTFaHaxPvkMFoMstKQzpHtf5LEfbFqD81xW74LuabnfqesjYyj1wbAmeBpAqBajQFeKzuCtr4LrjvzQHNNvUWD9hCxYZMNi9dSi4vxYTfvRjU89bviyX7vQ6KHG9MsRT4h2nF5NwSYgEBXXHVJUrSKnNnpcZTTFzzvZuc8GDKnuNRywnt9Uf6UMtCibSz2VsJ1wpmdkSwhwfFEy6MrheBPJzR3X2niLK7QEApbtihVS6mxAToheGBNJpG989fpTfNXP33o7nA8emxa6yQ2J6Q6qCeES3DBcboKNrcFBBb6caiqiGJ8CYizkhPosp3p47NBxUeV9j9xNHUvvp2UvCrakE7BPPNRDmJJse2cD4bGxg2G4DyYE8qXMbaaz5qADaYy9PPyfFejWeC8PHmGpFTMJkc',
    '__cf_bm': 'yvaaq4yZ.8pYYgOHNY6j7on2NaVB4vRDdhv2QM3ijOE-1688560576-0-ARHDDvXj0wiqOJWMkWyjaG1NhH4FTYgZW7ZV4dBqo9bk3iA/DudwBEXY9XCmSX96JRkDtnG42AySNRINu4ro4KSPZ8UJjp4oX+ERAJeJkOZLtkc4YJxw5fle59Rs7ihrdQ==',
    '__adal_ses': '*',
    'mp_dbbd7bd9566da85f012f7ca5d8c6c944_mixpanel': '%7B%22distinct_id%22%3A%20%22%24device%3A1892473e2ab45d1-053c63f6eadc4e-26031d51-144000-1892473e2ac45d1%22%2C%22%24device_id%22%3A%20%221892473e2ab45d1-053c63f6eadc4e-26031d51-144000-1892473e2ac45d1%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22X-Experiment-Id%22%3A%20%5B%0A%20%20%20%20%22sp_reordering_experiment%22%0A%5D%2C%22X-Variation-Id%22%3A%20%5B%0A%20%20%20%20%22sp_reordering_experiment_about_first%22%0A%5D%2C%22X-STS-DeviceId%22%3A%20%225daf0006-f522-460c-917c-61f91b063f85%22%7D',
    '_uetsid': '047995c01af211eeb35ca188cafe6f86',
    '_uetvid': '047a5bd01af211eeaf1c15097d937fec',
    '_ga': 'GA1.2.1984010866.1688533726',
    '_gat': '1',
    '_gat_UA-2056847-65': '1',
    '_ga_B0NS054E7V': 'GS1.1.1688560565.4.1.1688560887.50.0.0',
    '_scid_r': '66d7c34d-d672-46de-8fd6-33661f7ffd79',
    '__adal_id': '4a578c08-ee23-4be7-83c3-cccea855e3e9.1688533725.4.1688560888.1688558423.f82427b7-6879-4f73-8e6f-b9403fc5df16',
    'outbrain_cid_fetch': 'true',
}


def minutes_to_months(minutes):
    total_days = minutes / (24 * 60)
    delta = timedelta(days=total_days)
    reference_date = datetime(2013, 1, 1)
    target_date = reference_date + delta
    months = (target_date.year - reference_date.year) * 12 + (target_date.month - reference_date.month)
    return round(months, 2)


def get_ins():
    print("[+] Getting Required data...")
    params = {
        'bulkNumber': '1',
        'cv': 'c28c38bfb26d0b650777f5d398e4fae7_bd1ed52f2e4f9d8079285c280cca6f41',
        'totalBulks': '1',
    }

    response = requests.get(
        'https://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments/bulk',
        params=params,
        impersonate="chrome110",
    )
    jd = response.json()
    return {instrument['InstrumentID']: instrument['SymbolFull'] for instrument in jd['InstrumentDisplayDatas']}


def scrape_history(j):
    customer_id = j.get("CustomerId")
    # print(customer_id)
    username = j.get("UserName")
    print(f"[+] Scraping: {username}")

    response = requests.get(
        f'https://www.etoro.com/sapi/trade-data-real/history/public/credit/flat?StartTime={generate_datetime_one_year_back()}&PageNumber=1&ItemsPerPage=3000&PublicHistoryPortfolioFilter=&CID={customer_id}',
        cookies=cookies,
        impersonate="chrome100",
    )
    # print(f'[+] status: {response.status_code}')
    json_data = response.json()
    history = []

    for position in json_data['PublicHistoryPositions']:
        instrument_id = position['InstrumentID']
        if instrument_id in instrument_map:
            position['Name'] = instrument_map[instrument_id]
            history.append(position)

    return history


def frequent_trades(username, no_trades=3):
    params = {
        'CopyAsAsset': 'true',
        # 'client_request_id': 'ac2030bd-f140-4c11-9816-0b9531305767',
    }

    response = requests.get(
        f'https://www.etoro.com/sapi/userstats/stats/username/{username}/trades/oneYearAgo',
        params=params,
        cookies=cookies,
        impersonate="chrome110")
    json_data = response.json()
    over_all = json_data.get("all")
    trades = []
    for position in json_data['assets'][:no_trades]:
        instrument_id = position['instrumentId']
        if instrument_id in instrument_map:
            position['Name'] = instrument_map[instrument_id]
            trades.append(position)
    return {"all": over_all, "frequent": trades}


def get_active_since(cid):
    params = {
        'IncludeSimulation': 'true',
        # 'client_request_id': '1b748f77-455a-4de9-b5d8-9815b687989a',
    }

    response = requests.get(
        f'https://www.etoro.com/sapi/userstats/gain/cid/{cid}/history',
        params=params,
        cookies=cookies, impersonate="chrome110")
    jd = response.json()
    return monthly[0].get("start") if (monthly := jd.get("monthly")) else ""


def scrape_stats(j):
    customer_id = j.get("CustomerId")
    username = j.get("UserName")
    print(f"[+] Scraping Stats: {username}")

    params = {
        'Period': 'OneYearAgo',
        # 'client_request_id': 'c468c0b7-4f0c-4c11-b44f-652d5ac97fab',
    }

    response = requests.get(
        f'https://www.etoro.com/sapi/rankings/cid/{customer_id}/rankings/',
        params=params,
        cookies=cookies, impersonate="chrome110")
    jd = response.json().get("Data")
    rankings = {"Gain": jd.get("Gain"), "DailyGain": jd.get("DailyGain"), "ThisWeekGain": jd.get("ThisWeekGain"),
                "risk_score_yearly": jd.get("PeakToValley"), "risk_score_weekly": jd.get("WeeklyDD"),
                "risk_score_daily": jd.get("DailyDD"), "Copiers": jd.get("Copiers"),
                "Copy_value": jd.get("AUMTierDesc"), "CopiersGain": jd.get("CopiersGain"),
                "ProfitableWeeksPct": jd.get("ProfitableWeeksPct"),
                "trades_per_week": jd.get("Trades") / jd.get("ActiveWeeks")}
    trades_data = frequent_trades(username)
    rankings["frequent_trades"] = trades_data.get("frequent")
    rankings["overall_trades_stats"] = trades_data.get("all")
    rankings["avg_holding_months"] = minutes_to_months(trades_data.get("all").get("avgHoldingTimeInMinutes"))
    rankings["active_since"] = get_active_since(customer_id)
    return rankings


def get_real_time_rates():
    response = requests.get(
        'https://www.etoro.com/sapi/trade-real/instruments?InstrumentDataFilters=Rates',
        cookies=cookies, impersonate="chrome110")

    jd = response.json()

    return {rate['InstrumentID']: {"Ask": rate.get("Ask"), "Bid": rate.get("Bid")} for rate in jd.get("Rates")}


def scrape_portfolio(j):
    customer_id = j.get("CustomerId")
    username = j.get("UserName")
    print(f"[+] Scraping portfolio: {username}")
    params = {
        'cid': customer_id,
        # 'client_request_id': '81bb71f0-083a-4ffd-b01a-53c25a70dff7',
    }

    response = requests.get(
        'https://www.etoro.com/sapi/trade-data-real/live/public/portfolios',
        params=params,
        cookies=cookies, impersonate="chrome110")

    jd = response.json()
    portfolios = []
    rates = get_real_time_rates()
    for p in jd.get("AggregatedPositions"):
        instrument_id = p['InstrumentID']
        if instrument_id in instrument_map:
            p['Name'] = instrument_map[instrument_id]
            p["ask"] = rates[instrument_id].get("Ask")
            p["bid"] = rates[instrument_id].get("Bid")
            portfolios.append(p)

    return portfolios


def get_user_data(username):
    response = requests.get(
        f'https://www.etoro.com/api/logininfo/v1.1/users/{username}',
        cookies=cookies, impersonate="chrome110")
    jd = response.json()

    return {"CustomerId": jd.get("realCID"),
            "UserName": jd.get("username")}


if __name__ == '__main__':
    input_user = input("Enter Username:").strip()
    usr_data = get_user_data(input_user)
    instrument_map = get_ins()
    history = scrape_history(usr_data)
    stats = scrape_stats(usr_data)
    portfolio = scrape_portfolio(usr_data)

    out_jd = {'PublicHistoryPositions': history, "stats": stats, "portfolio": portfolio}
    with open(f"{folder_path}/{usr_data.get('UserName')}.json", "w", encoding="utf-8") as f:
        json.dump(out_jd, f, indent=3)
