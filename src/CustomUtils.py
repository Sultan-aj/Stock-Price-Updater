import threading
import logging

# Ensure that a logger is setup
logger = logging.getLogger(__name__)

def summaryCard(drivers, threads):
    """
    Displays a summary card with details about active threads and web driver instances.
    
    Args:
    drivers (dict): A dictionary containing driver instances.
    threads (dict): A dictionary containing thread instances.
    """
    logger.info("\n" + "="*60)
    logger.info("{:^60}".format("System Summary"))
    logger.info("="*60)
    
    # Count and log active threads
    active_threads = threading.enumerate()
    logger.info("{:<40} {:>20}".format("Total active threads:", len(active_threads)))
    logger.info("{:<40} {:>20}".format("Active WebDriver instances:", len(drivers)))

    # Log details of threads managed within this application
    logger.info("\n" + "-"*60)
    logger.info("{:^60}".format("Managed Thread Details"))
    logger.info("-"*60)
    for symbol, thread_info in threads.items():
        status = "Running" if thread_info.is_alive() else "Stopped"
        logger.info("{:<15} {:<20} {:>25}".format(symbol, f"Status: {status}", f"ID={thread_info.ident}"))

    # Optionally, log all system active threads details
    logger.info("\n" + "-"*60)
    logger.info("{:^60}".format("All Active Threads in System"))
    logger.info("-"*60)
    for thread in active_threads:
        logger.info("{:<20} {:<20} {:>20}".format(thread.name, "Alive" if thread.is_alive() else "Dead", f"ID={thread.ident}" ))

    logger.info("="*60 + "\n")
