# assignment_onebyzero# 


---

## What’s This All About?
This app:
- Watches a folder for new transaction `.csv` files every 5 Minutes.
- Have API endpoints to fetch transactions and summaries by city and products.
- Logs everything to files and your console.

---

## Project Structure
transaction-api/
├── app.py                  # The Flask main file 
├── config.py               # config file
├── data_controller.py      # data controller where data management happens
├── file_processor.py       # process new files every 5 minutes
├── logger.py               # logs everything
├── models.py               # defined models for our objects
├── transactions/           # Where transaction CSVs comes in 
├── reference/              # Holds product data
│   └── products.csv        # Product files
└── README.md               # Readme file
