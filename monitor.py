import json
import time
import sys
from typing import Dict, Any, Set, Tuple
from datetime import datetime, timedelta

from api_client import NiftyAPIClient, SymbolConfig
from formatters import get_middle_slice, format_option_data, format_totals
from db_handler import MongoDBHandler
from market_schedule import MarketSchedule

class ResponseCache:
    def __init__(self):
        self.previous_responses = {}
    
    def is_different_response(self, symbol: str, new_response: str) -> bool:
        if symbol not in self.previous_responses or new_response != self.previous_responses[symbol]:
            self.previous_responses[symbol] = new_response
            return True
        print(f"Received identical API response for {symbol} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return False

class OptionsMonitor:
    def __init__(self, interval_seconds: int = 2):
        self.interval_seconds = interval_seconds
        # Initialize with default Nifty configuration
        self.api_client = NiftyAPIClient()
        self.cache = ResponseCache()
        self.db_handler = MongoDBHandler()
        self.market_schedule = MarketSchedule()
        self.last_time_display = None
        # Load existing records from DB once at startup
        self.existing_records: Set[Tuple[float, str]] = self.db_handler.get_existing_records()

    def process_data(self, symbol: str, result_data: Dict[str, Any], records_count: int):
        # Get middle N records from opDatas based on configuration
        middle_options = get_middle_slice(result_data["opDatas"], records_count)
        
        # Format option chain data
        formatted_data = [format_option_data(option) for option in middle_options]
        
        # Format totals data
        totals = format_totals(result_data["opTotals"])
        
        return formatted_data, totals

    def print_summary(self, symbol: str, totals: Dict[str, Any], formatted_data: list, new_records: bool):
        print(f"\n=== Data Check for {symbol.upper()} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        if new_records:
            print("New records found and saved to database.")
            print("\nOverall Totals:")
            print(json.dumps(totals["Total"], indent=2))
            print("\nFirst Strike Price Data:")
            print(json.dumps(formatted_data[0], indent=2))
        else:
            print("No new records found. Skipping database update.")
        
        print("\n" + "="*50)

    def display_remaining_time(self):
        """Display the remaining time until market open/close that updates in-place"""
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Get the status and remaining time
        if self.market_schedule.is_market_open():
            seconds_remaining = self.market_schedule.time_until_market_close()
            remaining_time = str(timedelta(seconds=seconds_remaining)).split('.')[0]  # Format as HH:MM:SS
            status = f"MARKET OPEN - Closes in {remaining_time}"
        else:
            seconds_remaining = self.market_schedule.time_until_market_open()
            remaining_time = str(timedelta(seconds=seconds_remaining)).split('.')[0]  # Format as HH:MM:SS
            status = f"MARKET CLOSED - Opens in {remaining_time}"
        
        # Only update if display has changed
        display_text = f"Current Time: {current_time} | {status}"
        if display_text != self.last_time_display:
            # Move cursor to the beginning of the line and clear the line
            sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear the line with more spaces
            sys.stdout.write(display_text)
            sys.stdout.flush()
            
            self.last_time_display = display_text

    def wait_for_market_open(self):
        """Wait until market opens if it's currently closed"""
        if not self.market_schedule.is_market_open():
            print(f"\nMarket is currently closed. Waiting until market opens...")
            
            # Sleep in shorter intervals to allow for keyboard interruption and update the clock
            max_sleep_time = 1  # Update clock every second
            while not self.market_schedule.is_market_open():
                seconds_until_open = self.market_schedule.time_until_market_open()
                if seconds_until_open <= 0:
                    break
                    
                sleep_duration = min(seconds_until_open, max_sleep_time)
                time.sleep(sleep_duration)
                
                # Update the remaining time display
                self.display_remaining_time()
                
                # Print periodic updates about wait time (every 5 minutes)
                if seconds_until_open % 300 == 0 and seconds_until_open > 0:
                    wait_time = timedelta(seconds=seconds_until_open)
                    print()  # Move to new line after the clock
                    print(f"Still waiting {wait_time} until market opens.")
            
            print("\nMarket is now open! Starting monitoring...")
            return True
        return False

    def run(self):
        print(f"Starting options monitoring with market hours check...")
        print(f"Loaded {len(self.existing_records)} existing records from database")
        print(f"Monitoring symbols: {', '.join(str(config) for config in self.api_client.symbols_config)}")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                try:
                    # Display remaining time until market open/close
                    self.display_remaining_time()
                    
                    # Check if market is open
                    if not self.market_schedule.is_market_open():
                        if self.wait_for_market_open():
                            continue
                    
                    # Get remaining time until market close
                    seconds_until_close = self.market_schedule.time_until_market_close()
                    if seconds_until_close is not None and seconds_until_close < 60:
                        print(f"\nMarket closing in less than 60 seconds. Stopping monitoring.")
                        print("Will resume when market reopens.")
                        self.wait_for_market_open()
                        continue
                    
                    # Record the start time of the cycle
                    cycle_start_time = time.time()
                    
                    # Fetch new data for all symbols
                    results = self.api_client.fetch_option_chain()
                    
                    for symbol, result_data in results.items():
                        if result_data:
                            # Find the configuration for this symbol
                            symbol_config = next((config for config in self.api_client.symbols_config 
                                               if config.symbol == symbol), None)
                            if not symbol_config:
                                continue

                            # Check if response is same as previous
                            if not self.cache.is_different_response(symbol, str(result_data)):
                                continue
                                
                            formatted_data, totals = self.process_data(symbol, result_data, symbol_config.records_count)
                            
                            # Check if there are any new records that don't exist in our cached set
                            has_new_records = False
                            for option in formatted_data:
                                strike_price = option['Strike Price']
                                time_value = option['Time']
                                if (strike_price, time_value) not in self.existing_records:
                                    has_new_records = True
                                    break
                                
                            # Only proceed with database operations if we have new records
                            if has_new_records:
                                # Update existing records with newly saved ones
                                self.existing_records = self.db_handler.save_data(
                                    formatted_data, 
                                    totals,
                                    self.existing_records
                                )
                                
                                # Print summary on a new line (after the clock)
                                print()  # Move to new line after the clock
                                self.print_summary(symbol, totals, formatted_data, True)
                            else:
                                print(f"\n=== Data Check for {symbol.upper()} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
                                print("Skipping database update - All records already exist in database")
                                print("=" * 50)
                    
                    # Calculate how long to wait until next cycle
                    cycle_duration = time.time() - cycle_start_time
                    wait_time = max(0, self.interval_seconds - cycle_duration)
                    if wait_time > 0:
                        time.sleep(wait_time)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"\nError during monitoring: {e}")
                    time.sleep(self.interval_seconds)
        
        finally:
            self.db_handler.close()
            print("\nMonitoring stopped by user")