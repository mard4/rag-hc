## create tables with info about patients, appointments, and doctors, chat
## todo: updated timestamp

from connection import *
conn, cur = get_connection()

query_patients = """CREATE TABLE IF NOT EXISTS patients (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    surname VARCHAR(100),
                    sex VARCHAR(10),
                    birth_date DATE,
                    address VARCHAR(255),
                    phone_number VARCHAR(20) UNIQUE,
                    email VARCHAR(100) UNIQUE,
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

cur.close()
conn.close()