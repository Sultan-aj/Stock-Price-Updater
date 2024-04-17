import logging
import logging.handlers
import os
from datetime import datetime

class CustomLoggingHandler(logging.handlers.RotatingFileHandler):
    """
    A custom rotating file handler that rotates logs based on file size.
    Upon rotation, the logs are renamed with the date and a sequential number and moved to the archive folder.
    """
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0, archive_folder='archive'):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.archive_folder = archive_folder
        self.baseFilename = os.path.abspath(filename)  # Ensure full path is used

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        # Ensure the archive directory exists
        if not os.path.exists(self.archive_folder):
            os.makedirs(self.archive_folder)

        # Format current time in the file name
        current_time = datetime.now().strftime("%Y_%m_%d")
        root, ext = os.path.splitext(self.baseFilename)
        
        # Find the next available file number for today's date
        count = 1
        new_filename = f"{root}_{current_time}_{count}{ext}"
        new_filename = os.path.join(self.archive_folder, os.path.basename(new_filename))

        while os.path.exists(new_filename):
            count += 1
            new_filename = f"{root}_{current_time}_{count}{ext}"
            new_filename = os.path.join(self.archive_folder, os.path.basename(new_filename))
        
        # Rename the old log file to the new filename in the archive directory
        os.rename(self.baseFilename, new_filename)

        if not self.delay:
            self.stream = self._open()

def setup_logging(log_directory='./logs', log_filename='stock_price_updater.log', max_log_size=5*1024*1024, backup_count=5):
    """
    Set up the logging configuration with archiving.
    """
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_path = os.path.join(log_directory, log_filename)
    archive_path = os.path.join(log_directory, "archive")  # Define the archive directory path
    
    # Create a custom rotating file handler with archive support
    handler = CustomLoggingHandler(
        log_path, maxBytes=max_log_size, backupCount=backup_count, archive_folder=archive_path
    )
    
    # Define a formatter and set it to the handler
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
    handler.setFormatter(formatter)
    
    # Get the root logger and set the handler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger

# Example usage, if needed directly for tests or standalone setups
if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Test log entry")
