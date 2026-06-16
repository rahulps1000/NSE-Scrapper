import requests

nse_api_url = "https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol={symbol}&expiry={expiry_date}"

def fetch_option_chain(symbol, expiry_date):
    url = nse_api_url.format(symbol=symbol, expiry_date=expiry_date)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")