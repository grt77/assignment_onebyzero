# assignment_onebyzero# 


---

## What’s This All About?
This app:
- Watches a folder for new transaction `.csv` files every 5 Minutes.
- Have API endpoints to fetch transactions and summaries by city and products.
- Logs everything to files and your console.

---

## Project Structure
```
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
```

#Command to run script

```
python app.py

```

Endpoints to fetch data

```

1. /assignment/transaction/<transaction_id>

sample output : 
{
  "productName": "Product1",
  "transactionAmount": 1000,
  "transactionDatetime": "2025-04-01 10:00:00",
  "transactionId": "t1"
}


2-/assignment/transactionSummaryByProducts/<int:last_n_days>

sample output : 

[
  {
    "productName": "Product1",
    "totalAmount": 30000
  },
  {
    "productName": "Product2",
    "totalAmount": 30000
  }
]

3-/assignment/transactionSummaryByManufacturingCity/<int:last_n_days>'
sample output :

[
  {
    "cityName": "Los Angeles",
    "totalAmount": 30000
  },
  {
    "cityName": "New York",
    "totalAmount": 30000
  }
]

```


```
