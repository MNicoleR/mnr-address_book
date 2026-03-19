from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import math
from contextlib import contextmanager, asynccontextmanager

@asynccontextmanager
async def lifespan(address_book_app: FastAPI):
    init_db()
    yield

address_book_app = FastAPI(title="Address Book API", desc="Address Book API for EV Assessment - Robbins", lifespan=lifespan)

#database file to be created
DB_FILE = "address.db"

#class containing details of the address
class Address(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

#initializing the db
def init_db():
    with get_db_connection() as conn:
        conn.execute("""
                CREATE TABLE IF NOT EXISTS addresses (
                     address_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     city TEXT NOT NULL,
                     country TEXT NOT NULL,
                     longitude REAL NOT NULL,
                     latitude REAL NOT NULL)
                     """)
        

# get all currently existing addresses
@address_book_app.get("/getAddresses", response_model=List[Address])
async def getAddresses():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM addresses")
        rows = cursor.fetchall()

    address = [
        Address(
            id=row['address_id'],
            name=row['name'],
            city=row['city'],
            country=row['country'],
            longitude=row['longitude'],
            latitude=row['latitude']
        )

        for row in rows
    ]

    return address


#creating a new address
@address_book_app.post("/createAddress", response_model=Address, status_code=201)
async def create_address(address: Address):

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                INSERT INTO addresses (name, city, country, longitude, latitude)
                       VALUES (?, ?, ?, ?, ?)
                       """, (address.name, address.city, address.country, address.longitude, address.latitude))
        conn.commit()

        address_id = cursor.lastrowid

        cursor.execute("SELECT * FROM addresses WHERE address_id = ?", (address_id,))
        row = cursor.fetchone()

        return Address(
            id=row['address_id'],
            name=row['name'],
            city=row['city'],
            country=row['country'],
            longitude=row['longitude'],
            latitude=row['latitude']
        )


# updating the address according the address id
@address_book_app.put("/updateAddress/{address_id}", response_model=Address)
async def update_address(address_id: int, address_update: Address):
    

    #building update query dynamically according to what needs to be updated
    update_fields = []
    update_values = []

    if address_update.name is not None and address_update.name != "":
        update_fields.append("name = ?")
        update_values.append(address_update.name)
    if address_update.city is not None and address_update.city != "":
        update_fields.append("city = ?")
        update_values.append(address_update.city)
    if address_update.country is not None and address_update.country != "":
        update_fields.append("country = ?")
        update_values.append(address_update.country)
    if address_update.longitude is not None:
        update_fields.append("longitude = ?")
        update_values.append(address_update.longitude)
    if address_update.latitude is not None:
        update_fields.append("latitude = ?")
        update_values.append(address_update.latitude)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No valid fields for updating address were given")
    
    update_values.append(address_id)

    with get_db_connection() as conn:

        #checking if the address to be updated exists in the db
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM addresses WHERE address_id = ?", (address_id,))
        row = cursor.fetchone

        if row is None:
            raise HTTPException(status_code=404, detail="Address not found.")
        
        #updating address
        address_query = f"UPDATE addresses SET {', '.join(update_fields)} WHERE address_id = ?"
        cursor.execute(address_query, update_values)
        conn.commit()

        cursor.execute("SELECT * FROM addresses WHERE address_id = ?", (address_id,))
        row = cursor.fetchone()

        return Address(
            id=row['address_id'],
            name=row['name'],
            city=row['city'],
            country=row['country'],
            longitude=row['longitude'],
            latitude=row['latitude']
        )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(address_book_app, host="0.0.0.0", port=8000)






    






