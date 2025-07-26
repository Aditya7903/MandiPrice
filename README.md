# AgMarknet API

A Flask-based API for fetching agricultural commodity price data from the [AgMarknet website](https://agmarknet.gov.in/). This API provides easy access to commodity prices across different states and markets in India.

## Features

- Fetch commodity prices from AgMarknet
- Support for multiple commodities, states, and markets
- Returns data in JSON format
- Robust error handling with fallback mechanisms
- No browser automation required
- Fast and reliable data retrieval

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agmarknetAPI.git
   cd agmarknetAPI
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the API server:
   ```bash
   python APIwebScrapingPopUp.py
   ```

2. The API will be available at:
   - Local: http://127.0.0.1:5000
   - Network: http://your-ip-address:5000

### Available Endpoints

1. **Home Page**
   ```
   GET /
   ```
   Returns information about available commodities, states, and usage instructions.

2. **Price Data**
   ```
   GET /request?commodity=COMMODITY&state=STATE&market=MARKET
   ```
   Returns price data for the specified commodity, state, and market.

### Example Requests

1. Get potato prices in Bangalore, Karnataka:
   ```
   http://127.0.0.1:5000/request?commodity=Potato&state=Karnataka&market=Bangalore
   ```

2. Get tomato prices in Pune, Maharashtra:
   ```
   http://127.0.0.1:5000/request?commodity=Tomato&state=Maharashtra&market=Pune
   ```

### Example Response

```json
[
  {
    "S.No": "1",
    "Date": "02-Apr-2025",
    "Market": "Bangalore",
    "Commodity": "Potato",
    "Variety": "General",
    "Min Price": "1200",
    "Max Price": "1800",
    "Modal Price": "1500"
  }
]
```

## Available Commodities

- Potato
- Tomato
- Onion
- Rice
- Wheat
- Maize
- Apple
- Banana
- Orange
- Mango
- Grapes
- Watermelon
- Coconut
- Sugarcane
- Cotton
- Jute
- Coffee
- Tea
- Milk
- Egg
- Fish
- Chicken
- Mutton
- Beef
- Pork

## Available States

- Karnataka
- Maharashtra
- Gujarat
- Tamil Nadu
- Uttar Pradesh
- And others as per AgMarknet's database

## Error Handling

The API includes robust error handling:
- Returns appropriate error messages for missing parameters
- Provides fallback data when direct scraping fails
- Logs errors for debugging purposes

## Dependencies

- Flask: Web framework
- BeautifulSoup4: HTML parsing
- Requests: HTTP requests
- Other dependencies listed in requirements.txt

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data source: [AgMarknet](https://agmarknet.gov.in/)
- Built with Flask and Python

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
