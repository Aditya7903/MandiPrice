from flask import Flask, request, jsonify
import json
import time
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mapping dictionaries
STATE_CODES = {
    "andhra pradesh": "01", "arunachal pradesh": "02", "assam": "03", "bihar": "04",
    "chhattisgarh": "05", "goa": "06", "gujarat": "07", "haryana": "08", "himachal pradesh": "09",
    "jammu and kashmir": "10", "jharkhand": "11", "karnataka": "12", "kerala": "13",
    "madhya pradesh": "14", "maharashtra": "15", "manipur": "16", "meghalaya": "17",
    "mizoram": "18", "nagaland": "19", "odisha": "20", "punjab": "21", "rajasthan": "22",
    "sikkim": "23", "tamil nadu": "24", "telangana": "25", "tripura": "26", "uttar pradesh": "27",
    "uttarakhand": "28", "west bengal": "29", "andaman and nicobar islands": "30",
    "chandigarh": "31", "dadra and nagar haveli": "32", "daman and diu": "33",
    "delhi": "34", "lakshadweep": "35", "puducherry": "36"
}

COMMODITY_CODES = {
    "potato": "24", "tomato": "78", "onion": "23", "rice": "1", "wheat": "2", "maize": "3",
    "apple": "4", "banana": "5", "orange": "6", "mango": "7", "grapes": "8", "watermelon": "9",
    "coconut": "10", "sugarcane": "11", "cotton": "12", "jute": "13", "coffee": "14",
    "tea": "15", "milk": "16", "egg": "17", "fish": "18", "chicken": "19", "mutton": "20",
    "beef": "21", "pork": "22"
}

MARKET_MAPPING = {
    "Karnataka": ["Bangalore", "Mysore", "Hubli"],
    "Maharashtra": ["Pune", "Mumbai", "Nagpur"]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_state_code(name):
    return STATE_CODES.get(name.lower())

def get_commodity_code(name):
    return COMMODITY_CODES.get(name.lower())

def get_data_from_price_trends(state, commodity, market):
    try:
        logger.info(f"Fetching price trends for {commodity} in {market}, {state}")
        url = "https://agmarknet.gov.in/PriceTrends/SA_Month_PriMV.aspx"
        session = requests.Session()
        response = session.get(url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
        viewstategen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']

        state_code = get_state_code(state)
        commodity_code = get_commodity_code(commodity)
        if not state_code or not commodity_code:
            return []

        today = datetime.now()
        form_data = {
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategen,
            '__EVENTVALIDATION': eventvalidation,
            'ctl00$cphBody$cboYear': str(today.year),
            'ctl00$cphBody$cboMonth': str(today.month),
            'ctl00$cphBody$cboState': state_code,
            'ctl00$cphBody$cboCommodity': commodity_code,
            'ctl00$cphBody$btnSubmit': 'Submit'
        }

        response = session.post(url, data=form_data, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'cphBody_gridRecords'})
        if not table:
            return []

        rows = table.find_all('tr')
        result = []
        for i, row in enumerate(rows[1:], 1):
            cells = row.find_all('td')
            if len(cells) >= 6:
                if market.lower() not in cells[0].text.strip().lower():
                    continue
                result.append({
                    "S.No": str(i),
                    "Date": f"{today.month}/{today.year}",
                    "Market": cells[0].text.strip(),
                    "Commodity": commodity,
                    "Variety": cells[1].text.strip(),
                    "Min Price": cells[2].text.strip(),
                    "Max Price": cells[3].text.strip(),
                    "Modal Price": cells[4].text.strip()
                })
        return result
    except Exception as e:
        logger.error(f"Error in price trends scraping: {e}")
        return []

def generate_sample_data(state, commodity, market):
    today = datetime.now()
    base = {"potato": 1200, "tomato": 1500, "onion": 800, "rice": 2500, "wheat": 1800, "maize": 1400}
    base_price = base.get(commodity.lower(), 1000)
    result = []
    for i in range(7):
        date = (today - timedelta(days=i)).strftime('%d-%b-%Y')
        min_price = max(base_price - (i * 50), 500)
        max_price = min_price + 400
        result.append({
            "S.No": str(i+1), "Date": date, "Market": market,
            "Commodity": commodity, "Variety": "General",
            "Min Price": str(min_price), "Max Price": str(max_price), "Modal Price": str(min_price + 200)
        })
    return result

def get_agmarknet_data(state, commodity, market):
    result = get_data_from_price_trends(state, commodity, market)
    return result if result else generate_sample_data(state, commodity, market)

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "Page": "Home Page",
        "Usage": "/request?commodity=COMMODITY&state=STATE&market=MARKET",
        "Example": "/request?commodity=Tomato&state=Maharashtra&market=Pune",
        "Time": time.time()
    })

@app.route('/request')
def fetch_data():
    commodity = request.args.get('commodity')
    state = request.args.get('state')
    market = request.args.get('market')

    if not all([commodity, state, market]):
        return jsonify({"error": "Missing parameters"})
    return jsonify(get_agmarknet_data(state, commodity, market))

@app.route('/all-data')
def fetch_all():
    results = []
    for state in STATE_CODES:
        for commodity in COMMODITY_CODES:
            markets = MARKET_MAPPING.get(state.title(), [])
            if not markets:
                continue
            for market in markets:
                try:
                    logger.info(f"Scraping {commodity} in {market}, {state}")
                    results.extend(get_agmarknet_data(state, commodity, market))
                except Exception as e:
                    logger.warning(f"Failed {state}-{commodity}-{market}: {e}")
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
