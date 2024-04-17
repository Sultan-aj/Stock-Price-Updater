# Selenium-based Stock Monitoring System

This project is designed to continuously monitor stock prices using Selenium and Python, updating them in real-time and managing multiple stocks using multi-threading. It includes features for dynamic thread management based on stock activity and comprehensive logging for debugging and monitoring.

## Features

- **Real-time Stock Price Monitoring**: Fetches real-time stock prices using Selenium with headless Chrome browsers.
- **Dynamic Thread Management**: Manages threads dynamically based on a JSON configuration file that specifies active stocks.
- **Advanced Logging**: Detailed logging system that records all significant events and errors, with enhanced visibility into thread operations.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Selenium WebDriver
- ChromeDriver compatible with your Chrome version



### Installation

1. **Clone the repository:**
   ```bash
   git clone https://yourrepositorylink.git
   cd SLEMMarketDataFetcher
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```




### Usage

1. **Modify the `stocks.json` to include the stocks you want to monitor.**

2. **Run the main script to start monitoring:**
   ```bash
   python main.py
   ```

3. **Check logs for detailed output and monitoring:**
   ```bash
   tail -f stock_price_updater.log
   ```
