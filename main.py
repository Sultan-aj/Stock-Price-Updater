import json
import os
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import queue

from src.CustomUtils import summaryCard
from src.StockWatcher import EventHandler
from src.LoggingHandler import setup_logging 


 

update_queue = queue.Queue()  # Create a queue for Excel updates

def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    service = Service(executable_path="./chromedriver-win64/chromedriver.exe" ,log_path='./logs/chromedriver.log', service_args=['--verbose'])
    return webdriver.Chrome(service=service, options=chrome_options)

def fetch_price(driver, url):
    try:
        driver.get(url)
        price = driver.find_element(By.CSS_SELECTOR, ".market-summary__last-price").text
        return price
    except Exception as e:
        logger.error(f"Error fetching price: {str(e)}")
        return None

# Global lock for thread safety
json_output_lock = threading.Lock()

def update_json_output(symbol, price):
    with json_output_lock:  # Ensure only one thread can execute this block at a time
        try:
            # Try to read the existing data
            try:
                with open('./output/stock_prices_output.json', 'r') as file:
                    data = json.load(file)
            except FileNotFoundError:
                # If the file does not exist, start with an empty dictionary
                data = {}
            except json.JSONDecodeError:
                # If there is an error decoding the file, log the error and start with an empty dictionary
                logger.error("Error decoding the JSON file. Starting with an empty dictionary.")
                data = {}

            # Update the data with the new price
            data[symbol] = {'price': price, 'last_updated': datetime.datetime.now().isoformat()}
            logger.info(f"Json file updated for {symbol} with price {price} at {datetime.datetime.now().isoformat()}")


            # Write the updated data back to the file
            with open('./output/stock_prices_output.json', 'w') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error updating JSON output: {str(e)}")

def monitor_stock(symbol, url, stop_event, driver):
    logger.debug(f"Thread started for {symbol}")
    while not stop_event.is_set():
        price = fetch_price(driver, url)
        if price:
            # Put the symbol and price into the queue
            update_queue.put((symbol, price))
        for _ in range(30):  # 300 seconds total, checking every 10 seconds
            if stop_event.is_set():
                break
            time.sleep(10)
    logger.info(f"Closing Thread for {symbol}")
    driver.quit()
    

def process_queue():
    while True:
        symbol, price = update_queue.get()
        update_json_output(symbol, price)
        update_queue.task_done()
        

def load_stock_data(filepath='/assets/stocks.json'):
    with open(filepath, 'r') as file:
        return json.load(file)['metadata']



def on_file_change(threads, stop_events, drivers,  filepath):

    logger.info("File change detected, updating threads.")
    new_stock_data = load_stock_data(filepath)
    
    # Excluding the queue thread from being stopped or removed
    special_threads = ['QUEUE_THREAD']
    
    # Stop threads that are no longer active
    for symbol in list(threads.keys()):
        if symbol in special_threads:  # Skip special threads like QUEUE_THREAD
            continue
        
        if not any(s['symbol'] == symbol and s['isActive'] for s in new_stock_data):
            logger.info(f"Stopping thread for: {symbol}")
            stop_events[symbol].set()
            threads[symbol].join(timeout=10)
            if threads[symbol].is_alive():
                logger.warning(f"Thread {symbol} did not stop as expected.")
            else:
                del threads[symbol]
                del stop_events[symbol]
    # Start new threads for newly activated stocks
    for stock in new_stock_data:
        if stock['isActive'] and stock['symbol'] not in threads:
            logger.info(f"Starting new thread for: {stock['symbol']}")
            stop_events[stock['symbol']] = threading.Event()
            driver = setup_browser()
            drivers[stock['symbol']] = driver 
            thread = threading.Thread(target=monitor_stock, args=(stock['symbol'], stock['link'], stop_events[stock['symbol']], driver))
            thread.start()
            threads[stock['symbol']] = thread
    
    


def setup_file_watcher(filepath, threads, stop_events, drivers):
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
     
    print(f"directory name ==> {directory}")
    def callback():
        on_file_change(threads, stop_events, drivers, filepath)
        # Display summary card
        summaryCard(drivers, threads)

    event_handler = EventHandler(filepath, callback)
    observer = Observer()
    observer.schedule(event_handler=event_handler, path=directory, recursive=False)
    observer.start()
    return observer


def main(filepath='assets/stocks.json'):
    
    stock_data = load_stock_data(filepath)
    threads = {}
    stop_events = {}
    
    drivers = {}

    

    
     # Start the queue processing thread
    queue_thread = threading.Thread(target=process_queue, daemon=True)
    queue_thread.start()
    
    threads["QUEUE_THREAD"] = queue_thread

    for stock in stock_data:
        if stock['isActive']:
            symbol = stock['symbol']
            stop_events[symbol] = threading.Event()
            driver = setup_browser()
            drivers[symbol] = driver
            thread = threading.Thread(target=monitor_stock, args=(symbol, stock['link'], stop_events[symbol], driver))
            thread.start()
            threads[symbol] = thread
    
    summaryCard(drivers, threads)
    
    observer = setup_file_watcher(filepath, threads, stop_events, drivers)

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        for event in stop_events.values():
            event.set()
        for thread in threads.values():
            thread.join()
        observer.stop()
    finally:
        observer.join()
        
if __name__ == "__main__":
    print("Starting Program.....")
    logger = setup_logging()

    logger.info("***************** Starting Program *********************")
    main()
    logger.info("******************* END Program ************************")

