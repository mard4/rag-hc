from connection import *
conn, cur = get_connection()
import random
from datetime import datetime, timedelta
import bcrypt


query_patients = """CREATE TABLE IF NOT EXISTS patients (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    surname VARCHAR(100),
                    sex VARCHAR(10),
                    birth_date DATE,
                    address VARCHAR(255),
                    phone_number VARCHAR(20) UNIQUE,
                    email VARCHAR(100) UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );"""

query_doctors = """CREATE TABLE IF NOT EXISTS doctors (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        surname VARCHAR(100),
                        sex VARCHAR(10),
                        birth_date DATE,
                        address VARCHAR(100),
                        phone_number VARCHAR(20),
                        email VARCHAR(100) UNIQUE,
                        specialization VARCHAR(100),
                        experience_years INT,
                        rating FLOAT CHECK (rating >= 0 AND rating <= 5),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """

query_bookings = """CREATE TABLE IF NOT EXISTS bookings (
                    id SERIAL PRIMARY KEY,
                    patient_id INT REFERENCES patients(id),
                    doctor_id INT REFERENCES doctors(id),
                    appointment_date TIMESTAMP,
                    reason_for_visit TEXT,
                    status VARCHAR(20) DEFAULT 'scheduled', 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );"""

query_chat = """CREATE TABLE IF NOT EXISTS chat (
                id SERIAL PRIMARY KEY,
                patient_id INT REFERENCES patients(id),
                doctor_id INT REFERENCES doctors(id),
                message TEXT,
                answer TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

def create_tables(cur,conn, query_patients, query_doctors, query_bookings, query_chat):
    try:
        cur.execute(query_patients)
        cur.execute(query_doctors)
        cur.execute(query_bookings)
        cur.execute(query_chat)

        conn.commit()
        print("Tables patients, doctors, chat, bookings created successfully.")
    except Exception as e:
        print(f"Error creating tables {e}")
        conn.rollback()

#### === Doctors === ####
def populate_tables(cur, conn):
    patients = [
        ("Tung", "Sahur", "male", "2007-07-07", "Via Ballerina Cappuccina 5",    "3310000005", "tung@tung.com", "tung"),
    ]
    for name, surname, sex, birth, addr, phone, email, plain_pw in patients:
        # genera un salt e l’hash
        salt   = bcrypt.gensalt()  
        hashed = bcrypt.hashpw(plain_pw.encode("utf-8"), salt).decode("utf-8")
        cur.execute("""
            INSERT INTO patients
              (name, surname, sex, birth_date, address, phone_number, email, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (name, surname, sex, birth, addr, phone, email, hashed))
    conn.commit()

    doctors = [
        ("Mary",  "Mani", "female", "1982-11-22", "Via Duomo 2",   "3390000002", "mar.d@clinic.com", "Dermatology",   10, 4.3),
        ("Kekko",    "Sa",  "male",   "1975-06-15", "Via Po 3",         "3390000003", "k.sa@clinic.com",    "Neurology",     12, 4.5),
        ("Anna",  "Pepe",   "female", "1988-01-05", "Via Larga 4",      "3390000004", "a.pe@clinic.com",   "Pediatrics",    8,  4.9),    ]
    for d in doctors:
        cur.execute("""
            INSERT INTO doctors
              (name, surname, sex, birth_date, address, phone_number, email, specialization, experience_years, rating)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING;
        """, d)

    conn.commit()

### === 
if __name__ == "__main__":
    conn, cur = get_connection()
    create_tables(cur,conn, query_patients, query_doctors, query_bookings, query_chat)
    populate_tables(cur, conn)
    cur.close()
    conn.close()