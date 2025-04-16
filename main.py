from monitor import OptionsMonitor
from health_server import HealthServer
from api_client import SymbolConfig, NiftyAPIClient

if __name__ == "__main__":
    # Start health check server for Docker
    health_server = HealthServer(port=8000)
    health_server.start()
    
    try:
        # Create configurations for multiple symbols
        symbols_config = [
            SymbolConfig("nifty", "2025-04-24", 20),  # Default Nifty configuration
            SymbolConfig("adanient", "", 10),  # Adani Enterprises
            SymbolConfig("adanigreen", "", 10),  # Adani Green Energy
            SymbolConfig("adaniports", "", 10),  # Adani Ports
            SymbolConfig("apollohosp", "", 10),  # Apollo Hospitals
            SymbolConfig("asianpaint", "", 10),  # Asian Paints
            SymbolConfig("axisbank", "", 10),  # Axis Bank
            SymbolConfig("bajaj-auto", "", 10),  # Bajaj Auto
            SymbolConfig("bajfinance", "", 10),  # Bajaj Finance
            SymbolConfig("bajajfinsv", "", 10),  # Bajaj Finserv
            SymbolConfig("bpcl", "", 10),  # BPCL
            SymbolConfig("bhartiartl", "", 10),  # Bharti Airtel
            SymbolConfig("britannia", "", 10),  # Britannia
            SymbolConfig("cipla", "", 10),  # Cipla
            SymbolConfig("coalindia", "", 10),  # Coal India
            SymbolConfig("divislab", "", 10),  # Divi's Labs
            SymbolConfig("drreddy", "", 10),  # Dr Reddy's Labs
            SymbolConfig("eichermot", "", 10),  # Eicher Motors
            SymbolConfig("grasim", "", 10),  # Grasim
            SymbolConfig("hcltech", "", 10),  # HCL Tech
            SymbolConfig("hdfcbank", "", 10),  # HDFC Bank
            SymbolConfig("hdfclife", "", 10),  # HDFC Life
            SymbolConfig("heromotoco", "", 10),  # Hero MotoCorp
            SymbolConfig("hindalco", "", 10),  # Hindalco
            SymbolConfig("hindunilvr", "", 10),  # Hindustan Unilever
            SymbolConfig("icicibank", "", 10),  # ICICI Bank
            SymbolConfig("indusindbk", "", 10),  # IndusInd Bank
            SymbolConfig("infy", "", 10),  # Infosys
            SymbolConfig("itc", "", 10),  # ITC
            SymbolConfig("jswsteel", "", 10),  # JSW Steel
            SymbolConfig("kotakbank", "", 10),  # Kotak Bank
            SymbolConfig("ltim", "", 10),  # LTIMindtree
            SymbolConfig("lt", "", 10),  # Larsen & Toubro
            SymbolConfig("m&m", "", 10),  # Mahindra & Mahindra
            SymbolConfig("maruti", "", 10),  # Maruti Suzuki
            SymbolConfig("nestleind", "", 10),  # Nestle India
            SymbolConfig("ntpc", "", 10),  # NTPC
            SymbolConfig("ongc", "", 10),  # ONGC
            SymbolConfig("powergrid", "", 10),  # Power Grid
            SymbolConfig("reliance", "", 10),  # Reliance Industries
            SymbolConfig("sbilife", "", 10),  # SBI Life Insurance
            SymbolConfig("sbin", "", 10),  # State Bank of India
            SymbolConfig("sunpharma", "", 10),  # Sun Pharma
            SymbolConfig("tataconsum", "", 10),  # Tata Consumer
            SymbolConfig("tatamotors", "", 10),  # Tata Motors
            SymbolConfig("tatasteel", "", 10),  # Tata Steel
            SymbolConfig("tcs", "", 10),  # TCS
            SymbolConfig("techm", "", 10),  # Tech Mahindra
            SymbolConfig("titan", "", 10),  # Titan Company
            SymbolConfig("ultracemco", "", 10),  # UltraTech Cement
            SymbolConfig("upl", "", 10),  # UPL
            SymbolConfig("wipro", "", 10),  # Wipro
        ]
        
        # Initialize API client with configurations
        api_client = NiftyAPIClient(symbols_config)
        
        # Start the options monitoring with configured symbols
        monitor = OptionsMonitor(interval_seconds=2)
        monitor.api_client = api_client  # Use our configured API client
        monitor.run()
    finally:
        # Stop health server on exit
        health_server.stop()
