from kafka import KafkaProducer
import json
import time
import yfinance as yf  # Yahoo Finance library

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize data to JSON
)

#live stock data from Yahoo Finance
def get_stock_data(symbol='AAPL'):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d', interval='1m')

        if not data.empty:
            latest_price = data['Close'].dropna().iloc[-1]  # Get last closing price
            latest_timestamp = data.index[-1].strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp

            return {
                'symbol': symbol,
                'price': round(latest_price, 2),
                'timestamp': latest_timestamp
            }
        else:
            print(f"No data received for {symbol}")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Send data to Kafka topic 'TestTopic'
def send_data_to_kafka():
    while True:
        stock_data = get_stock_data('AAPL')  # Fetch stock data for AAPL

        if stock_data:
            producer.send('TestTopic', stock_data)
            print(f"Sent data: {stock_data}")

        time.sleep(60)  # Fetch every 1 minute

# Start sending data to Kafka
if __name__ == "__main__":
    send_data_to_kafka()
