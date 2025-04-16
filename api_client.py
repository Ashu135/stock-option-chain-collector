import requests
from typing import Dict, Any, Optional, List
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SymbolConfig:
    def __init__(self, symbol: str, expiry_date: str, records_count: int = 20):
        self.symbol = symbol.lower()
        self.expiry_date = expiry_date
        self.records_count = records_count
        
    def __str__(self):
        return f"{self.symbol} (Expiry: {self.expiry_date}, Records: {self.records_count})"

class NiftyAPIClient:
    def __init__(self, symbols_config: Optional[List[SymbolConfig]] = None):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        self.url = "https://webapi.niftytrader.in/webapi/option/option-chain-data"
        
        # Default configuration if none provided
        self.symbols_config = symbols_config or [
            SymbolConfig("nifty", "2025-04-24", 20)
        ]
        
        # Create a session with retry logic
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        
    def fetch_option_chain_for_symbol(self, config: SymbolConfig) -> Optional[Dict[str, Any]]:
        """Fetch option chain data for a single symbol"""
        params = {
            "symbol": config.symbol,
            "exchange": "nse",
            "expiryDate": config.expiry_date,
            # Calculate atmAbove and atmBelow based on records_count
            "atmBelow": str(config.records_count // 2),
            "atmAbove": str(config.records_count // 2)
        }
        
        try:
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
            print(f"Error fetching data for {config.symbol}: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing data for {config.symbol}: {e}")
            return None
        except ValueError as e:
            print(f"Error decoding JSON for {config.symbol}: {e}")
            return None
        
        return None
        
    def fetch_option_chain(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """Fetch option chain data for all configured symbols"""
        results = {}
        
        for config in self.symbols_config:
            results[config.symbol] = self.fetch_option_chain_for_symbol(config)
                
        return results
    
    def add_symbol(self, symbol: str, expiry_date: str, records_count: int = 20):
        """Add a new symbol configuration"""
        config = SymbolConfig(symbol, expiry_date, records_count)
        self.symbols_config.append(config)
        
    def remove_symbol(self, symbol: str):
        """Remove a symbol configuration"""
        symbol = symbol.lower()
        self.symbols_config = [config for config in self.symbols_config if config.symbol != symbol]
        
    def update_symbol(self, symbol: str, expiry_date: Optional[str] = None, records_count: Optional[int] = None):
        """Update configuration for an existing symbol"""
        symbol = symbol.lower()
        for config in self.symbols_config:
            if config.symbol == symbol:
                if expiry_date is not None:
                    config.expiry_date = expiry_date
                if records_count is not None:
                    config.records_count = records_count
                return True
        return False
        
    def __del__(self):
        # Close the session when the object is destroyed
        if hasattr(self, 'session'):
            self.session.close()