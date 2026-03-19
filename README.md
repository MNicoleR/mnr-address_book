# address_book

A python address book project using FastAPI that supports create, update, and search of addresses. 

## Requirements

- Python
- FastAPI
- Uvicorn
- Pydantic

## How to run

1. Navigate to the address_book directory
```bash
cd address_book
```

2. Install dependencies
```bash
pip install -r requirements.txt
```
note: best practice to use venv

3. Start the server
```bash
python main.py
```

The API can be called on `http://localhost:8000`

## To run the different APIs

1. Get Addresses
```bash
curl -X GET http://localhost:8000/getAddresses
```

2. Create an Address
```bash
curl -X POST http://localhost:8000/createAddress -H "Content-Type: application/json" -d '{
        "name": "Jane Doe",
        "city": "Pasig",
        "country": "Philippines",
        "longitude": "40.01923",
        "latitude": "-80.012313"
}'
```

3. Update an Address
```bash
curl -X PUT http://localhost:8000/updateAddress/1 -H "Content-Type: application/json" -d '{
        "city": "Taguig",
        "latitude": "-80.012313",
        "longitude": "40.0000"
}'

```