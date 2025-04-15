# Nifty Options Chain Collector

A Python application that collects and analyzes Nifty options chain data from the NSE (National Stock Exchange of India).

## Features

- **Market-Aware Operation**: Automatically runs only during market hours (9:15 AM to 3:30 PM IST, Monday to Friday)
- **Real-time Data Collection**: Fetches options chain data every 2 seconds
- **Duplicate Prevention**: Avoids storing duplicate records to save storage space
- **MongoDB Integration**: Stores data efficiently for future analysis
- **Docker Support**: Easily deployable using Docker

## Architecture

The application is built with modularity in mind:

- **API Client**: Handles communication with the Nifty options data source
- **Formatters**: Processes and formats the raw data
- **Database Handler**: Manages MongoDB operations
- **Market Schedule**: Tracks market hours
- **Monitoring System**: Orchestrates the data collection process

## Requirements

- Python 3.10+
- MongoDB
- Docker (optional)

## Installation

### Without Docker

1. Clone the repository:

   ```
   git clone https://github.com/Ashu135/stock-option-chain-collector.git
   cd stock-option-chain-collector
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Make sure MongoDB is running on your machine

4. Run the application:
   ```
   python main.py
   ```

### With Docker

1. Clone the repository:

   ```
   git clone https://github.com/Ashu135/stock-option-chain-collector.git
   cd stock-option-chain-collector
   ```

2. Make sure MongoDB is running on your machine

3. Build and run the Docker container:
   ```
   docker-compose up -d
   ```

## Data Structure

The application collects and stores:

- Strike price details (calls and puts)
- Open interest (OI) data
- Volume data
- Put-Call ratio
- Greeks (delta, gamma, theta, etc.)

## MongoDB Collections

- **strike_prices**: Contains individual option contract data
- **totals_data**: Contains aggregated market data

## Querying Data

You can analyze collected data using MongoDB queries. Example:

```python
from datetime import datetime, timedelta
from db_handler import MongoDBHandler

# Initialize the database handler
db = MongoDBHandler()

# Get data for a specific strike price
strike_data = db.query_strike_price(18000)

# Get data for a specific strike price within a time range
yesterday = datetime.now() - timedelta(days=1)
strike_data = db.query_strike_price(18000, start_time=yesterday)

# Get statistics for a strike price
stats = db.get_strike_price_stats(18000)
```

## License

MIT

## Author

Ashu135
