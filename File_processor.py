import threading
import csv
import os
import time
from config import Config
from data_contoller import DataController
from logger import Logger



class FileProcessor:
    def __init__(self, data_controller):
        self.transaction_dir = Config.TRANSACTION_DIR
        self.logging=Logger("INFO")
        if not os.path.exists(self.transaction_dir):
            os.makedirs(self.transaction_dir)
            self.logging.info(f"Created transaction directory: {self.transaction_dir}")
        self.data_controller = data_controller
        self.stop_event = threading.Event()
        self.processor_thread = threading.Thread(target=self._process_transaction_files)
        self.processor_thread.start()
        self.logging.info("File processor started.")

    def _process_transaction_files(self):
        processed_files = set()
        while not self.stop_event.is_set():
            self.logging.info("Checking for new files...")
            try:
                for filename in os.listdir(self.transaction_dir):
                    if filename.endswith('.csv') and filename not in processed_files:
                        filepath = os.path.join(self.transaction_dir, filename)
                        self._process_file(filepath)
                        processed_files.add(filename)
            except Exception as e:
                self.logging.error(f"Error in file processing loop: {e}")
            self.logging.info(f"Waiting {Config.WATCH_INTERVAL} seconds before next check...")
            time.sleep(Config.WATCH_INTERVAL)

    def _process_file(self, filepath):
        self.logging.info(f"Processing file: {filepath}")
        try:
            with self.data_controller.write_lock:
                with open(filepath, 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    self.logging.info(f"File {filepath} has {len(rows)} rows.")
                    for row in rows:
                        self.data_controller.add_transaction(row)
                self.data_controller.swap_readble_data()
                self.logging.info(f"Processed file: {filepath}")
        except Exception as e:
            self.logging.error(f"Error processing file {filepath}: {e}")

    def stop(self):
        self.logging.info("Stopping file processor...")
        self.stop_event.set()
        self.processor_thread.join()
        self.logging.info("File processor stopped.")