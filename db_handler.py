from pymongo import MongoClient, ASCENDING
from datetime import datetime
import os
from typing import Dict, Any, List, Set, Tuple

class MongoDBHandler:
    def __init__(self):
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        # Add connection pooling configuration
        self.client = MongoClient(
            mongodb_uri,
            maxPoolSize=50,  # Maximum number of connections in the pool
            minPoolSize=10,  # Minimum number of connections kept open
            waitQueueTimeoutMS=2000,  # How long to wait for an available connection
            connectTimeoutMS=5000,  # How long to wait for a connection to be established
            serverSelectionTimeoutMS=5000  # How long to wait for server selection
        )
        self.db = self.client['nifty_options']
        self.strike_collection = self.db['strike_prices']
        self.totals_collection = self.db['totals_data']
        
        # Create indexes for faster querying
        self.strike_collection.create_index([("timestamp", ASCENDING)])
        self.strike_collection.create_index([("strike_price", ASCENDING)])
        self.strike_collection.create_index([("strike_price", ASCENDING), ("timestamp", ASCENDING)])
        self.strike_collection.create_index([("strike_price", ASCENDING), ("time", ASCENDING)])
        
        self.totals_collection.create_index([("timestamp", ASCENDING)])
    
    def get_existing_records(self) -> Set[Tuple[float, str]]:
        """
        Get all existing strike price and time combinations from the database
        Returns a set of tuples (strike_price, time)
        """
        existing_records = set()
        cursor = self.strike_collection.find({}, {"strike_price": 1, "time": 1, "_id": 0})
        
        for doc in cursor:
            if "strike_price" in doc and "time" in doc:
                existing_records.add((doc["strike_price"], doc["time"]))
        
        print(f"Loaded {len(existing_records)} existing records from database")
        return existing_records
    
    def save_data(self, options_data: List[Dict[str, Any]], totals_data: Dict[str, Any], 
                  existing_records: Set[Tuple[float, str]]) -> Set[Tuple[float, str]]:
        """
        Save options and totals data to MongoDB with timestamp.
        Each strike price is saved as a separate document for easier querying.
        Returns updated set of existing records.
        """
        timestamp = datetime.now()
        
        # Save each strike price as a separate document
        strike_documents = []
        new_records_added = 0
        
        for option in options_data:
            strike_price = option['Strike Price']
            time_value = option['Time']
            
            # Skip if this strike price and time combination already exists
            if (strike_price, time_value) in existing_records:
                continue
                
            # This is a new record, add to the list for insertion
            strike_document = {
                'timestamp': timestamp,
                'strike_price': strike_price,
                'expiry': option['Expiry'],
                'pcr': option['PCR'],
                'symbol': option['Symbol'],
                'index_close': option['Index Close'],
                'time': time_value,
                'calls': option['Calls'],
                'puts': option['Puts']
            }
            strike_documents.append(strike_document)
            
            # Add to the set of existing records
            existing_records.add((strike_price, time_value))
            new_records_added += 1
        
        # Insert all new strike documents
        if strike_documents:
            self.strike_collection.insert_many(strike_documents)
            
            # Save totals data only if we have new strike documents
            totals_document = {
                'timestamp': timestamp,
                'data': totals_data
            }
            self.totals_collection.insert_one(totals_document)
            
            print(f"Data saved to MongoDB at {timestamp} - {new_records_added} new strike prices")
        else:
            print(f"No new records to save at {timestamp}")
        
        return existing_records
    
    def query_strike_price(self, strike_price: float, start_time=None, end_time=None):
        """
        Query data for a specific strike price with optional time range.
        Returns data in chronological order.
        """
        query = {"strike_price": strike_price}
        
        # Add time range if provided
        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time
            if end_time:
                query["timestamp"]["$lte"] = end_time
        
        return list(self.strike_collection.find(query).sort("timestamp", ASCENDING))
    
    def batch_query_strike_prices(self, strike_prices: List[float], start_time=None, end_time=None, batch_size=100):
        """
        Query data for multiple strike prices with optional time range.
        Uses batching to efficiently retrieve large datasets.
        """
        all_results = []
        
        # Create base query
        base_query = {}
        if start_time or end_time:
            base_query["timestamp"] = {}
            if start_time:
                base_query["timestamp"]["$gte"] = start_time
            if end_time:
                base_query["timestamp"]["$lte"] = end_time
        
        # Process in batches for better memory management
        for i in range(0, len(strike_prices), batch_size):
            batch = strike_prices[i:i+batch_size]
            query = {**base_query, "strike_price": {"$in": batch}}
            
            # Execute batch query
            batch_results = list(self.strike_collection.find(query).sort("timestamp", ASCENDING))
            all_results.extend(batch_results)
        
        return all_results
        
    def get_strike_price_stats(self, strike_price: float, start_time=None, end_time=None):
        """
        Get aggregate statistics for a specific strike price over time
        """
        query = {"strike_price": strike_price}
        
        # Add time range if provided
        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time
            if end_time:
                query["timestamp"]["$lte"] = end_time
        
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$strike_price",
                "avg_pcr": {"$avg": "$pcr"},
                "max_calls_oi": {"$max": "$calls.OI"},
                "max_puts_oi": {"$max": "$puts.OI"},
                "avg_calls_volume": {"$avg": "$calls.Volume"},
                "avg_puts_volume": {"$avg": "$puts.Volume"},
                "first_timestamp": {"$min": "$timestamp"},
                "last_timestamp": {"$max": "$timestamp"},
                "count": {"$sum": 1}
            }}
        ]
        
        results = list(self.strike_collection.aggregate(pipeline))
        return results[0] if results else None
    
    def close(self) -> None:
        """Close the MongoDB connection"""
        self.client.close()