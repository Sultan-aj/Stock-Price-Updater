import os
import time
from watchdog.events import FileSystemEventHandler
import logging

logger = logging.getLogger(__name__)

class StockWatcher(FileSystemEventHandler):
    def __init__(self, filepath, callback):
        self.filepath = filepath
        self.callback = callback

    def on_modified(self, event):
        # Logging when a file modification is detected
        logging.info(f"Detected change in file: {event.src_path}")
        if event.src_path == self.filepath:
            self.callback()


class EventHandler(FileSystemEventHandler):
    
    def __init__(self, filepath, callback):
        self.filepath = filepath
        self.callback = callback
        
    def on_any_event(self,event):
        logger.info(f"Watchdog received event - {event.event_type} at {event.src_path}")
        
        if event.event_type in ['modified', 'created']: #and event.src_path == self.filepath:
            logger.info(f"Relevant modification detected in file: {event.src_path}")
            time.sleep(10)
            self.callback()
        elif event.event_type == 'deleted':
                logger.info(f"File was deleted: {event.src_path}")
                self.handle_deletion()
        else:
            logger.info(f"Watchdog received event - {event.event_type} at {event.src_path}")

        
    def on_created(self, event):
        print("Watchdog received created event - % s." % event.src_path)
        # Event is created, you can process it now
 
    def on_modified(self, event):
        # logger when a file modification is detected
        logger.info(f"Detected change in file: {event.src_path}")
        if event.src_path == self.filepath:
            self.callback()
 
    def handle_deletion(self):
        # Here you can attempt to reattach the observer or handle the situation appropriately
        # For example, you could wait for the file to be recreated or trigger a re-setup of the observer
        time.sleep(1)  # Small delay to avoid rapid re-checking
        if os.path.exists(self.filepath):
            logger.info("File reappeared: Reattaching observer.")
            self.callback()
        else:
            logger.error("File deleted and not restored.")
