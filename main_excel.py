import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import threading
import time
import logging
import queue
import argparse 
import datetime




# Setup basic configuration for logging
logging.basicConfig(filename='stock_price_updater.log', level=logging.DEBUG, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

update_queue = queue.Queue()  # Create a queue for Excel updates

def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    service = Service(executable_path="./chromedriver-win64/chromedriver.exe")  # Update path to your Chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def is_market_open(driver):
    driver.get("https://english.mubasher.info/countries/ae")
    try:
        # Assuming there's a specific div with classes that include either '--open' or '--close'
        market_status = driver.find_element(By.XPATH, '//*[@id="wrapper"]/div/div[1]/header/div[2]/div[3]/div[1]/div[2]/div/div[1]/span')
        if '--open' in market_status.get_attribute("class"):
            logging.info(f"Market is Open")
            return True
        else:
            logging.info(f"Market is Closed")
            return False
    except Exception as e:
        logging.error(f"Error checking market status: {str(e)}")
        return False  # Assume closed if there's an error

# function to wait every 30 min
def wait_until_next_half_hour():
    now = datetime.datetime.now()
    next_half_hour = now.replace(minute=5, second=0, microsecond=0)
    if now.minute >= 30:
        next_half_hour = next_half_hour.replace(hour=now.hour + 1)
    wait_time = (next_half_hour - now).total_seconds()
    time.sleep(max(0, wait_time))

# Function to fetch stock price using headless Chrome
def fetch_price(symbol, url, driver):
    logging.info(f"Fetching price for {symbol} from {url}")
    try:
        
        logging.debug(f"Attempting to access URL: {url}")
        driver.get(url)
        
        # You will need to modify the selector to match the website's structure
        price = driver.find_element(By.CSS_SELECTOR, ".market-summary__last-price").text
        # driver.quit()
        
        logging.info(f"Price fetched for {symbol}: {price}")

        return price
    except Exception as e:
        logging.error(f"Error fetching price for {symbol}: {str(e)}")
        return None



# Update excel based on queue data
def update_excel(file_path):
    while True:
        task = update_queue.get()
        if task is None:  # None is used as a signal to stop the thread
            break
        symbol, price = task
        current_time = datetime.datetime.now()  # Get current date and time
        try:
            df = pd.read_excel(file_path)
            index = df.index[df['Stock'] == symbol].tolist()[0]

            df.at[index, 'Price'] = price
            df.at[index, 'Last Updated'] = current_time  # Update the last updated time

            with pd.ExcelWriter(file_path, mode='w') as writer:
                df.to_excel(writer, index=False)
            logging.info(f"Excel file updated for {symbol} with price {price} at {current_time}")
        except Exception as e:
            logging.error(f"Error updating Excel for {symbol}: {str(e)}")
        update_queue.task_done()
        

# Thread function
def thread_function(symbol, url, driver, stop_event):
    
    logging.debug(f"Thread started for {symbol}")
    while not stop_event.is_set():        
        if is_market_open(driver):
            price = fetch_price(symbol, url, driver)
            if price:
                update_queue.put((symbol, price))  # Put the update in the queue
                # update_excel(file_path, symbol, price)
            time.sleep(60)  # refresh every 60 seconds
        else:
            logging.info(f"Market is closed. Waiting until the next half hour to check again for {symbol}.")
            wait_until_next_half_hour()


def summaryCard(drivers):
    # To get the number of active threads
    print("********* Summary *************")
    active_threads = threading.enumerate()
    number_of_threads = len(active_threads)
    print(f"Number of active threads: {number_of_threads}")
    print(f"Number of active WebDriver instances: {len(drivers)}")
    logging.info(f"Number of active threads: {number_of_threads} | Number of active WebDriver instances: {len(drivers)}")

    print("*******************************")


def main(file_path):
    print("Starting Program.....")
    logging.info("***************** Starting Program *********************")
    
    stop_event = threading.Event()

    # file_path = './assets/demo.xlsx'
    drivers = {}
    # service = Service(executable_path="./chromedriver-win64/chromedriver.exe")

    df = pd.read_excel(file_path)
    
    # Start the Excel updater thread
    excel_thread = threading.Thread(target=update_excel, args=(file_path,))
    excel_thread.start()
    
    threads = []
    for index, row in df.iterrows():
        driver = setup_browser()
        drivers[row['Stock']] = driver
        t = threading.Thread(target=thread_function, args=(row['Stock'], row['URL'], driver, stop_event))
        t.start()
        threads.append(t)


    # displaying details
    summaryCard(drivers) 
    
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Ctrl+C pressed. Shutting down...")
        stop_event.set()
        for thread in threads:
            thread.join()
        update_queue.put(None)
        excel_thread.join()
        
    update_queue.put(None)
    excel_thread.join()

    logging.info("***************** END Program *********************")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stock Price Updater')
    parser.add_argument('-f', '--file', default='./assets/demo.xlsx', help='Excel file path')
    args = parser.parse_args()
    
    main(args.file)
   
   


    
    