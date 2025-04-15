import requests
from typing import Dict, Any, Optional
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class NiftyAPIClient:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        self.url = "https://webapi.niftytrader.in/webapi/option/option-chain-data"
        
        # Create a session with retry logic
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        
    def fetch_option_chain(self) -> Optional[Dict[str, Any]]:
        params = {
            "symbol": "nifty",
            "exchange": "nse",
            "expiryDate": "",
            "atmBelow": "0",
            "atmAbove": "0"
        }
        
        try:
            # Add timeout parameters and use session
            response = self.session.get(
                self.url, 
                headers=self.headers, 
                params=params,
                timeout=(5, 15)  # 5s connect timeout, 15s read timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data["result"] == 1 and data["resultMessage"] == "Success":
                return data["resultData"]
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing data: {e}")
            return None
        except ValueError as e:
            print(f"Error decoding JSON: {e}")
            return None
        
        return None
        
    def __del__(self):
        # Close the session when the object is destroyed
        if hasattr(self, 'session'):
            self.session.close()