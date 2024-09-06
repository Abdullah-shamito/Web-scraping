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


def get_resp_json(url, params=None):
    if not params:
        params = {}
    response = requests.get(
        url, params=params,
        headers=headers, impersonate='chrome120', timeout=None)
    print(response.status_code)
    return response.json()


def get_user_data(username):
    params = {
        'accessingFlavorId': '1',
        'limit': '5',
        'name': username,
        'flavor': 'global',
    }

    jd = get_resp_json('https://www.zulutrade.com/zulutrade-gateway/traderstats/v2/api/providers/search',
                       params=params)
    for user in jd:
        if user.get("name") == username:
            return user.get("providerId")


def get_history(trader_id, page=0):
    histories_data = []
    while True:
        print(f"[+] page: {page}")
        url = f'https://www.zulutrade.com/zulutrade-gateway/trading/api/providers/{trader_id}/trades/history?timeframe=365&page={page}&size=100&sort=dateClosed,desc'

        jd = get_resp_json(url)
        if page == 0:
            print(f"[*] Total elements: {jd.get('totalElements')}")

        if content := jd.get("content"):
            histories_data.extend(content)
        if not content:
            break
        else:
            page += 1
    return histories_data


# Main execution logic
if __name__ == '__main__':
    input_user = input("Enter Username: ").strip()
    usr_id = get_user_data(input_user)
    if usr_id:
        histories = get_history(usr_id)
        out_jd = {'PublicHistoryPositions': histories}
        with open(f"{folder_path}/{input_user}.json", "w", encoding="utf-8") as f:
            json.dump(out_jd, f, indent=3)

    else:
        print("Failed to get user data.")
