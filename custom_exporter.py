from prometheus_client import start_http_server, Gauge
import time
import random

print("🚀 Starting Custom Exporter...")

# Create metrics
temperature = Gauge('weather_temperature_celsius', 'Temperature in Celsius', ['city'])
humidity = Gauge('weather_humidity_percent', 'Humidity percentage', ['city']) 
pressure = Gauge('weather_pressure_hpa', 'Pressure in hPa', ['city'])
wind_speed = Gauge('weather_wind_speed_kmh', 'Wind speed in km/h', ['city'])
cloudiness = Gauge('weather_cloudiness_percent', 'Cloudiness percentage', ['city'])
visibility = Gauge('weather_visibility_km', 'Visibility in kilometers', ['city'])
uv_index = Gauge('weather_uv_index', 'UV index', ['city'])
precipitation = Gauge('weather_precipitation_mm', 'Precipitation in mm', ['city'])
wind_direction = Gauge('weather_wind_direction_degrees', 'Wind direction in degrees', ['city'])
feels_like = Gauge('weather_feels_like_celsius', 'Feels-like temperature', ['city'])

# API monitoring
api_status = Gauge('weather_api_status', 'API status (1=up, 0=down)')
api_requests = Gauge('weather_api_requests_total', 'Total API requests')
data_freshness = Gauge('weather_data_freshness_seconds', 'Data freshness in seconds')

CITIES = ["Astana", "Almaty", "London", "Paris", "Berlin", "Moscow", "Tokyo", "New York", "Dubai", "Sydney"]

def update_metrics():
    """Update all metrics"""
    try:
        print(f"📊 Updating metrics for {len(CITIES)} cities...")
        
        for city in CITIES:
            # Generate realistic weather data
            base_temp = random.uniform(-10, 35)
            
            temperature.labels(city=city).set(round(base_temp, 1))
            humidity.labels(city=city).set(random.randint(30, 95))
            pressure.labels(city=city).set(random.randint(980, 1030))
            wind_speed.labels(city=city).set(round(random.uniform(0, 20), 1))
            cloudiness.labels(city=city).set(random.randint(0, 100))
            visibility.labels(city=city).set(random.randint(1, 25))
            uv_index.labels(city=city).set(round(random.uniform(0, 11), 1))
            precipitation.labels(city=city).set(round(random.uniform(0, 10), 1))
            wind_direction.labels(city=city).set(random.randint(0, 360))
            feels_like.labels(city=city).set(round(base_temp + random.uniform(-5, 5), 1))
        
        # Update monitoring metrics
        api_status.set(1)
        api_requests.inc()
        data_freshness.set(0)
        
        print(f"✅ Successfully updated metrics at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating metrics: {e}")
        api_status.set(0)
        return False

if __name__ == '__main__':
    try:
        # Start HTTP server
        start_http_server(8000)
        print("🎯 Custom Exporter is running on port 8000")
        print("📍 Monitoring cities:", ", ".join(CITIES))
        
        update_count = 0
        
        # Main loop
        while True:
            update_metrics()
            update_count += 1
            print(f"🔄 Update #{update_count} completed")
            
            # Wait 20 seconds
            time.sleep(20)
            
    except KeyboardInterrupt:
        print("🛑 Exporter stopped by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")