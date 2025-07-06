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

#### === popolate tables with some data === ####
def populate_tables(cur, conn):
    patients = [
        ("Alice", "Rossi", "female", "1985-04-12", "Via Milano 1", "3310000001", "alice.rossi@example.com", "hash_pw1"),
        ("Bruno", "Bianchi", "male",   "1978-09-23", "Via Torino 2",  "3310000002", "bruno.bianchi@example.com", "hash_pw2"),
        ("Carla", "Verdi",  "female", "1992-12-05", "Via Napoli 3",  "3310000003", "carla.verdi@example.com",  "hash_pw3"),
        ("Diego", "Neri",   "male",   "1980-02-17", "Via Firenze 4", "3310000004", "diego.neri@example.com",   "hash_pw4"),
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
        ("Fabio",   "Russo",   "male",   "1970-03-10", "Corso Venezia 10", "3390000001", "fabio.russo@clinic.com",   "Cardiology",    15, 4.7),
        ("Giulia",  "Ferrari", "female", "1982-11-22", "Piazza Duomo 20",   "3390000002", "giulia.ferrari@clinic.com", "Dermatology",   10, 4.3),
        ("Luca",    "Romano",  "male",   "1975-06-15", "Via Po 30",         "3390000003", "luca.romano@clinic.com",    "Neurology",     12, 4.5),
        ("Marina",  "Greco",   "female", "1988-01-05", "Via Larga 40",      "3390000004", "marina.greco@clinic.com",   "Pediatrics",    8,  4.9),
        ("Stefano", "Fontana", "male",   "1969-08-28", "Via Manzoni 50",    "3390000005", "stefano.fontana@clinic.com","Orthopedics",   20, 4.2),
    ]
    for d in doctors:
        cur.execute("""
            INSERT INTO doctors
              (name, surname, sex, birth_date, address, phone_number, email, specialization, experience_years, rating)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING;
        """, d)

    conn.commit()

    # Preleva gli id appena inseriti
    cur.execute("SELECT id FROM patients ORDER BY id LIMIT 5;")
    patient_ids = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id FROM doctors ORDER BY id LIMIT 5;")
    doctor_ids  = [row[0] for row in cur.fetchall()]

    # appuntamenti (bookings)
    for i in range(5):
        pid = random.choice(patient_ids)
        did = random.choice(doctor_ids)
        appt = datetime.now() + timedelta(days=random.randint(1, 30))
        reason = f"Visita di controllo #{i+1}"
        cur.execute("""
            INSERT INTO bookings
              (patient_id, doctor_id, appointment_date, reason_for_visit)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT DO NOTHING;
        """, (pid, did, appt, reason))

    conn.commit()

    # 5 messaggi di chat
    for i in range(5):
        pid = random.choice(patient_ids)
        did = random.choice(doctor_ids)
        msg = f"Domanda di prova #{i+1}?"
        ans = f"Risposta di esempio #{i+1}."
        ts  = datetime.now() - timedelta(hours=random.randint(1, 72))
        cur.execute("""
            INSERT INTO chat
              (patient_id, doctor_id, message, answer, timestamp)
            VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING;
        """, (pid, did, msg, ans, ts))

    conn.commit()
    print("Tabelle popolate con dati di esempio.")
#### === popolate tables with some data === ####

### === 
if __name__ == "__main__":
    conn, cur = get_connection()
    create_tables(cur,conn, query_patients, query_doctors, query_bookings, query_chat)
    populate_tables(cur, conn)
    cur.close()
    conn.close()