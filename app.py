from flask import Flask, jsonify
from data_contoller import DataController
from File_processor import FileProcessor
from config import Config
import logging
import atexit 
from datetime import datetime
import os
from config import Config
import time
from logger import Logger



logr=Logger("INFO")

app = Flask(__name__)
data_controller = DataController()
data_controller.load_products_data()
file_processor = FileProcessor(data_controller)
data_controller.set_file_processor(file_processor)


@app.route('/assignment/transaction/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    result = data_controller.get_transaction_by_id(transaction_id)
    if result is None:
        return jsonify({'error': 'Transaction not found'}), 404
    return jsonify(result)

@app.route('/assignment/transactionSummaryByProducts/<int:last_n_days>', methods=['GET'])
def get_summary_by_products(last_n_days):
    result = data_controller.get_summary_by_products(last_n_days)
    return jsonify(result)

@app.route('/assignment/transactionSummaryByManufacturingCity/<int:last_n_days>', methods=['GET'])
def get_summary_by_city(last_n_days):
    result = data_controller.get_summary_by_city(last_n_days)
    return jsonify(result)

def shutdown_server():
    data_controller.stop()


@atexit.register
def on_application_exit():
    shutdown_server()

if __name__ == '__main__':
    try:
        app.run(host=Config.HOST, port=Config.PORT, threaded=True)
    except Exception as e:
        logr.error(f"Failed to start Flask app: {e}")