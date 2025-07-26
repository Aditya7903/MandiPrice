from flask import Flask, request, jsonify
import json
import time
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import os
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_state_code(state_name):
    state_mapping = {
        "andhra pradesh": "01", "arunachal pradesh": "02", "assam": "03", "bihar": "04",
        "chhattisgarh": "05", "goa": "06", "gujarat": "07", "haryana": "08", "himachal pradesh": "09",
        "jammu and kashmir": "10", "jharkhand": "11", "karnataka": "12", "kerala": "13",
        "madhya pradesh": "14", "maharashtra": "15", "manipur": "16", "meghalaya": "17",
        "mizoram": "18", "nagaland": "19", "odisha": "20", "punjab": "21", "rajasthan": "22",
        "sikkim": "23", "tamil nadu": "24", "telangana": "25", "tripura": "26", "uttar pradesh": "27",
        "uttarakhand": "28", "west bengal": "29", "andaman and nicobar islands": "30", "chandigarh": "31",
        "dadra and nagar haveli": "32", "daman and diu": "33", "delhi": "34", "lakshadweep": "35",
        "puducherry": "36"
    }
    return state_mapping.get(state_name.lower())

def get_commodity_code(commodity_name):
    commodity_mapping = {
        "potato": "24", "tomato": "78", "onion": "23", "rice": "1", "wheat": "2", "maize": "3",
        "apple": "4", "banana": "5", "orange": "6", "mango": "7", "grapes": "8", "watermelon": "9",
        "coconut": "10", "sugarcane": "11", "cotton": "12", "jute": "13", "coffee": "14", "tea": "15",
        "milk": "16", "egg": "17", "fish": "18", "chicken": "19", "mutton": "20", "beef": "21", "pork": "22"
    }
    return commodity_mapping.get(commodity_name.lower())

def get_data_from_price_trends(state, commodity, market):
    try:
        logger.info(f"Fetching price trends for {commodity} in {market}, {state}")

        url = "https://agmarknet.gov.in/PriceTrends/SA_Month_PriMV.aspx"
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Referer": "https://agmarknet.gov.in/",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive"
        }

        max_retries = 3
        delay = 2
        for attempt in range(max_retries):
            try:
                response = session.get(url, headers=headers)
                response.raise_for_status()
                break
            except RequestException as e:
                logger.warning(f"Attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)

        soup = BeautifulSoup(response.text, 'html.parser')
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']

        state_code = get_state_code(state)
        commodity_code = get_commodity_code(commodity)
        if not state_code or not commodity_code:
            logger.warning(f"Invalid state or commodity: {state}, {commodity}")
            return []

        today = datetime.now()
        month = today.month
        year = today.year
        form_data = {
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            'ctl00$cphBody$cboYear': str(year),
            'ctl00$cphBody$cboMonth': str(month),
            'ctl00$cphBody$cboState': state_code,
            'ctl00$cphBody$cboCommodity': commodity_code,
            'ctl00$cphBody$btnSubmit': 'Submit'
        }

        response = session.post(url, data=form_data, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'cphBody_gridRecords'}) or soup.find('table', {'id': 'gvReportData'})
        if not table:
            logger.warning("No data table found")
            return []

        rows = table.find_all('tr')
        if len(rows) <= 1:
            logger.warning("No data rows in the table")
            return []

        json_list = []
        for i, row in enumerate(rows[1:], 1):
            cells = row.find_all('td')
            if len(cells) >= 6:
                market_name = cells[0].text.strip()
                if market and market.lower() not in market_name.lower():
                    continue
                json_list.append({
                    "S.No": str(i),
                    "Date": f"{month}/{year}",
                    "Market": market_name,
                    "Commodity": commodity,
                    "Variety": cells[1].text.strip(),
                    "Min Price": cells[2].text.strip(),
                    "Max Price": cells[3].text.strip(),
                    "Modal Price": cells[4].text.strip()
                })

        logger.info(f"Collected {len(json_list)} records for {commodity} in {market}, {state}")
        return json_list

    except Exception as e:
        logger.error(f"Error in price trends scraping: {e}")
        return []

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to KrishiMitra API", "usage": "/request?commodity=Tomato&state=Maharashtra&market=Pune"})

@app.route('/request')
def fetch_data():
    commodity = request.args.get('commodity')
    state = request.args.get('state')
    market = request.args.get('market')

    if not commodity or not state or not market:
        return jsonify({"error": "Missing parameters"}), 400

    data = get_data_from_price_trends(state, commodity, market)
    return jsonify(data if data else {"message": "No data available"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
