from monitor import OptionsMonitor
from health_server import HealthServer

if __name__ == "__main__":
    # Start health check server for Docker
    health_server = HealthServer(port=8000)
    health_server.start()
    
    try:
        # Start the options monitoring
        monitor = OptionsMonitor(interval_seconds=2)
        monitor.run()
    finally:
        # Stop health server on exit
        health_server.stop()
