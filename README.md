# assignment_onebyzero# 


---

## What’s This All About?
This app:
- Watches a folder for new transaction `.csv` files every 5 Minutes.
- Have API endpoints to fetch transactions and summaries by city and products.
- Logs everything to files and your console.

---

## Project Structure

transaction-api/ ├── app.py # The Flask main file ├── config.py # Config file ├── data_controller.py # Data controller where data management happens ├── file_processor.py # Process new files every 5 minutes ├── logger.py # Logs everything ├── models.py # Defined models for our objects ├── transactions/ # Where transaction CSVs come in ├── reference/ # Holds product data │ └── products.csv # Product files └── README.md # Readme file