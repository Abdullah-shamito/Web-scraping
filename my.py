from flask import Flask, request, jsonify
from scraper import get_data
import os
import json

app = Flask(__name__)

DATA_DIR = "data"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "subscriptions.log")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(LOG_DIR):  # Ensure the log directory exists
    os.makedirs(LOG_DIR)

subscribed_companies = set()

def log_action(action, ticker, exchange):
    """Log user actions to a file."""
    print(f"Attempting to log: {action} {ticker} on {exchange}")  # Debug print
    try:
        with open(LOG_FILE, 'a') as log:
            log.write(f"{action} {ticker} on {exchange}\n")
        print(f"Logged: {action} {ticker} on {exchange}")  # Debug print
    except Exception as e:
        print(f"Error logging: {str(e)}")  # Debug print
subscribed_companies = set()

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    ticker = data['ticker']
    exchange = data['exchange']

    # Store it in memory
    subscribed_companies.add((ticker, exchange))
    log_action("Subscribed to", ticker, exchange)

    
    # Scrape the data and store it
    scraped_data = get_data(ticker, exchange)
    with open(os.path.join(DATA_DIR, f"{ticker}.json"), 'w', encoding='utf-8') as json_file:
        json.dump(scraped_data, json_file, ensure_ascii=False, indent=4)

    return jsonify({'message': 'Subscription request received!'}), 200

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.get_json()
    ticker = data['ticker']
    exchange = data['exchange']

    subscribed_companies.discard((ticker, exchange))
    log_action("Unsubscribed from", ticker, exchange)

    return jsonify({'message': 'Unsubscription request received!'}), 200
@app.route('/data', methods=['GET'])
def get_all_data():
    all_data = {}

    for file_name in os.listdir(DATA_DIR):
        if file_name.endswith('.json'):
            file_path = os.path.join(DATA_DIR, file_name)
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                ticker_name = os.path.splitext(file_name)[0]
                all_data[ticker_name] = data

    return jsonify(all_data), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
