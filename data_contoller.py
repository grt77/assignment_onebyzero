import threading
import csv
from datetime import datetime,timedelta
from models import DataStore,Transactions,Product
from collections import defaultdict,OrderedDict
from config import Config
from logger import Logger

class DataController:
    def __init__(self):
        self.readable_store=DataStore()
        self.processing_store=DataStore()
        self.read_lock=threading.RLock()
        self.write_lock=threading.RLock()
        self.prev_prodcut_version=0
        self.prev_city_version=0
        self.curr_product_version=0
        self.curr_city_version=0
        self.logger=Logger("INFO")
        self.cache={
            'by_products':{
                'daily':{},
                'aggregated':OrderedDict()
            },
            'by_city':{
                'daily':{},
                'aggregated':OrderedDict()
            }
        }
        self.max_agg_cache=10
        self.file_processor=None
    
    def set_file_processor(self, file_processor):
        self.file_processor = file_processor

    def load_products_data(self):
        try:
            product_file=Config.REFERENCE_FILE
            with open(product_file,"r") as f:
                self.logger.info(f"Loading the Product data File:-{product_file}")
                reader=csv.DictReader(f)
                for row in reader:
                    product=Product(row['productId'],row['productName'],row['productManufacturingCity'])
                    self.readable_store.products[row['productId']]=product
                    self.processing_store.products[row['productId']]=product
        except Exception as e:
            self.logger.error(str(e))
            
    
    def add_transaction(self,row):
        try:
            transaction=Transactions(row['transactionId'],row['productId'],row['transactionAmount'],row['transactionDatetime'])
            self.processing_store.transactions[row['transactionId']]=transaction
        except Exception as e:
            self.logger.error(str(e))

        

    def swap_readble_data(self):
        try:
            self.logger.info("JUST started swapping THE READBLE AND PROCESSING STORES")
            with self.write_lock:
                self.readable_store.transactions.update(self.processing_store.transactions)
                self.processing_store.transactions={} 
                self.curr_city_version+=1
                self.curr_product_version+=1
                self.logger.info("JUST completed swapping THE READBLE AND PROCESSING STORES")
        except Exception as e:
            self.logger.error(str(e))

    def get_transaction_by_id(self,transaction_id):
        try:
            with self.read_lock:
                transaction=self.readable_store.transactions.get(transaction_id)
                if not transaction:
                    return None
                product=self.readable_store.products.get(transaction.product_id,Product('','',''))
                return {
                   'transactionId': transaction.transation_id,
                    'productName': product.name,
                    'transactionAmount': transaction.amount,
                    'transactionDatetime': transaction.datetime.strftime('%Y-%m-%d %H:%M:%S')
                }
        except Exception as e:
            self.logger.error(str(e))
    
    def _compute_daily_summary_by_products(self,date_str):
        try:
            self.logger.info(f"caluclating the daily summary for products for date {date_str}")
            total_summary=defaultdict(float)
            for transaction in self.readable_store.transactions.values():
                if transaction.datetime.strftime('%Y-%m-%d') == date_str:
                    product = self.readable_store.products.get(transaction.product_id, Product('', '', ''))
                    total_summary[product.name] += float(transaction.amount)
            return dict(total_summary)
        except Exception as e:
            self.logger.error(str(e))
    
    def _compute_daily_Summary_by_city(self,date_str):
        try:
            self.logger.info(f"caluclating the daily summary for city for date {date_str}")
            total_summary=defaultdict(float)
            for transaction in self.readable_store.transactions.values():
                if transaction.datetime.strftime('%Y-%m-%d') == date_str:
                    product = self.readable_store.products.get(transaction.product_id, Product('', '', ''))
                    total_summary[product.city] += transaction.amount
            return dict(total_summary)
        except Exception as e:
            self.logger.error(str(e))


    def _aggregate_summary_by_products(self,last_n_days):
        try:
            cutoff_date = datetime.now() - timedelta(days=int(last_n_days) - 1) 
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
            current_date_str = datetime.now().strftime('%Y-%m-%d')
            if self.prev_prodcut_version!=self.curr_product_version:
                self.cache['by_products']['daily'][current_date_str] = self._compute_daily_summary_by_products(current_date_str)
                self.prev_prodcut_version=self.curr_product_version
            with self.write_lock:
                required_days = set()
                current = datetime.now()
                for i in range(last_n_days):
                    date_str = (current - timedelta(days=i)).strftime('%Y-%m-%d')
                    required_days.add(date_str)
                self.logger.info(f"caluclating the aggregate summary for products for required days {required_days}")
                daily_cache = self.cache['by_products']['daily']
                for date_str in required_days:
                    if date_str not in daily_cache:
                        self.cache['by_products']['daily'][date_str] = self._compute_daily_summary_by_products(date_str)
                best_overlap = 0
                best_n_days = None
                best_cached_date = None
                best_cached_summary = None
                best_cached_days = None
                agg_cache = self.cache['by_products']['aggregated']
                for cached_n_days in agg_cache:
                    cached_date, cached_summary = agg_cache[cached_n_days]
                    cached_days = set([cached_date])
                    for i in range(1, cached_n_days):
                        cached_days.add((datetime.strptime(cached_date, '%Y-%m-%d') - timedelta(days=i)).strftime('%Y-%m-%d'))    
                    overlap = len(cached_days & required_days)
                    if overlap > best_overlap or (overlap == best_overlap and len(cached_days) < len(best_cached_days)):
                        best_overlap = overlap
                        best_n_days = cached_n_days
                        best_cached_date = cached_date
                        best_cached_summary = cached_summary
                        best_cached_days = cached_days
                self.logger.info(f"best_cached_days-{best_cached_days}")
                self.logger.info(f"best_cached_summary-{best_cached_summary}")
                self.logger.info(f"best_cached_overlap-{best_overlap}")
                if best_n_days is not None:
                    total_summary = defaultdict(float)
                    for product_name, amount in best_cached_summary:
                        total_summary[product_name] = amount

                    days_to_add = required_days - best_cached_days
                    self.logger.info(f"days to add-{days_to_add}")
                    for date_str in days_to_add:
                        for product_name, amount in daily_cache[date_str].items():
                            total_summary[product_name] += amount

                    days_to_subtract = best_cached_days - required_days
                    self.logger.info(f"days to subtract-{days_to_subtract}")
                    for date_str in days_to_subtract:
                        for product_name, amount in daily_cache[date_str].items():
                            total_summary[product_name] -= amount
                    summary = sorted(total_summary.items(), key=lambda x: x[0])
                    if len(agg_cache) >= self.max_agg_cache:
                        agg_cache.popitem(last=False)
                    agg_cache[last_n_days] = (current_date_str, summary)
                    return summary
            total_summary = defaultdict(float)
            for date_str in required_days:
                for product_name, amount in daily_cache.get(date_str, {}).items():
                    total_summary[product_name] += amount
            summary = sorted(total_summary.items(), key=lambda x: x[0])
            if len(agg_cache) >= self.max_agg_cache:
                agg_cache.popitem(last=False)  
            agg_cache[last_n_days] = (current_date_str, summary)
            return summary
        except Exception as e:
            self.logger.error(str(e))
    


    def _aggregate_summary_by_city(self,last_n_days):
        try:
            cutoff_date = datetime.now() - timedelta(days=int(last_n_days) - 1) 
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
            current_date_str = datetime.now().strftime('%Y-%m-%d')
            if self.prev_prodcut_version!=self.curr_product_version:
                self.cache['by_products']['daily'][current_date_str] = self._compute_daily_summary_by_products(current_date_str)
                self.prev_prodcut_version=self.curr_product_version
            with self.write_lock:
                required_days = set()
                current = datetime.now()
                for i in range(last_n_days):
                    date_str = (current - timedelta(days=i)).strftime('%Y-%m-%d')
                    required_days.add(date_str)
                print("required_Days",required_days)
                daily_cache = self.cache['by_city']['daily']
                for date_str in required_days:
                    if date_str not in daily_cache:
                        self.cache['by_city']['daily'][date_str] = self._compute_daily_Summary_by_city(date_str)
                best_overlap = 0
                best_n_days = None
                best_cached_date = None
                best_cached_summary = None
                best_cached_days = None
                agg_cache = self.cache['by_city']['aggregated']
                for cached_n_days in agg_cache:
                    cached_date, cached_summary = agg_cache[cached_n_days]
                    cached_days = set([cached_date])
                    for i in range(1, cached_n_days):
                        cached_days.add((datetime.strptime(cached_date, '%Y-%m-%d') - timedelta(days=i)).strftime('%Y-%m-%d'))    
                    overlap = len(cached_days & required_days)
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_n_days = cached_n_days
                        best_cached_date = cached_date
                        best_cached_summary = cached_summary
                        best_cached_days = cached_days
                self.logger.info(f"best_cached_days-{best_cached_days}")
                self.logger.info(f"best_cached_summary-{best_cached_summary}")
                self.logger.info(f"best_cached_overlap-{best_overlap}")
                if best_n_days is not None:
                    total_summary = defaultdict(float)
                    for product_name, amount in best_cached_summary:
                        total_summary[product_name] = amount

                    days_to_add = required_days - best_cached_days
                    self.logger.info(f"days to add-{days_to_add}")
                    for date_str in days_to_add:
                        for product_name, amount in daily_cache[date_str].items():
                            total_summary[product_name] += amount

                    days_to_subtract = best_cached_days - required_days
                    self.logger.info(f"days to subtract-{days_to_subtract}")
                    for date_str in days_to_subtract:
                        for product_name, amount in daily_cache[date_str].items():
                            total_summary[product_name] -= amount
                    summary = sorted(total_summary.items(), key=lambda x: x[0])
                    if len(agg_cache) >= self.max_agg_cache:
                        agg_cache.popitem(last=False)
                    agg_cache[last_n_days] = (current_date_str, summary)
                    return summary
            total_summary = defaultdict(float)
            for date_str in required_days:
                for product_name, amount in daily_cache.get(date_str, {}).items():
                    total_summary[product_name] += amount
            summary = sorted(total_summary.items(), key=lambda x: x[0])
            if len(agg_cache) >= self.max_agg_cache:
                agg_cache.popitem(last=False)  
            agg_cache[last_n_days] = (current_date_str, summary)
            return summary
        except Exception as e:
            self.logger.error(str(e))

    
    def get_summary_by_products(self, last_n_days):
        try:
            last_n_days = int(last_n_days)
            summary = self._aggregate_summary_by_products(last_n_days)
            return [{'productName': k, 'totalAmount': v} for k, v in summary]
        except Exception as e:
            self.logger.error(str(e))

    def get_summary_by_city(self, last_n_days):
        try:
            last_n_days = int(last_n_days)
            summary = self._aggregate_summary_by_city(last_n_days)
            return [{'cityName': k, 'totalAmount': v} for k, v in summary]
        except Exception as e:
            self.logger.error(str(e))
    
    def stop(self):
        if self.file_processor:
            self.file_processor.stop()