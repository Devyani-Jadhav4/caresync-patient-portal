# day7_users_seed.py
# Creates login accounts for two doctors and two patients
# from existing data in the CareSync database.
# Passwords are hashed with bcrypt before storing.
#
# Run once:
#     python day7_users_seed.py

import mysql.connector
import bcrypt


# ─────────────────────────────────────────────────────────────────────────────
# Connect to the caresync database
# ─────────────────────────────────────────────────────────────────────────────

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="Admin@@12345",
    database="caresync"
)

cur = conn.cursor(dictionary=True)

print("Connected to caresync.")


# ─────────────────────────────────────────────────────────────────────────────
# Helper: hash a plain password
# ─────────────────────────────────────────────────────────────────────────────

def make_hash(plain_password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(
        plain_password.encode("utf-8"),
        salt
    ).decode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Pick two real doctors from the database
#
# IMPORTANT:
# Your doctor table has "name", NOT "full_name".
# ─────────────────────────────────────────────────────────────────────────────

cur.execute(
    "SELECT doctor_id, name FROM doctor LIMIT 2"
)

doctors = cur.fetchall()


if len(doctors) < 2:
    print("ERROR: Need at least 2 doctors in the database.")
    cur.close()
    conn.close()
    exit()


# ─────────────────────────────────────────────────────────────────────────────
# Pick two real patients from the database
#
# IMPORTANT:
# Your patient table has "name", NOT "full_name".
# ─────────────────────────────────────────────────────────────────────────────

cur.execute(
    "SELECT patient_id, name FROM patient LIMIT 2"
)

patients = cur.fetchall()


if len(patients) < 2:
    print("ERROR: Need at least 2 patients in the database.")
    cur.close()
    conn.close()
    exit()


# ─────────────────────────────────────────────────────────────────────────────
# Build the list of accounts to insert
# ─────────────────────────────────────────────────────────────────────────────

accounts = [

    {
        "email": "doctor1@caresync.local",
        "plain_password": "Doctor@1234",
        "role": "doctor",
        "linked_id": doctors[0]["doctor_id"],
        "name": doctors[0]["name"]
    },

    {
        "email": "doctor2@caresync.local",
        "plain_password": "Doctor@1234",
        "role": "doctor",
        "linked_id": doctors[1]["doctor_id"],
        "name": doctors[1]["name"]
    },

    {
        "email": "patient1@caresync.local",
        "plain_password": "Patient@1234",
        "role": "patient",
        "linked_id": patients[0]["patient_id"],
        "name": patients[0]["name"]
    },

    {
        "email": "patient2@caresync.local",
        "plain_password": "Patient@1234",
        "role": "patient",
        "linked_id": patients[1]["patient_id"],
        "name": patients[1]["name"]
    },

]


# ─────────────────────────────────────────────────────────────────────────────
# Insert each account
# Skip if email already exists
# ─────────────────────────────────────────────────────────────────────────────

for acc in accounts:

    # Check whether account already exists
    cur.execute(
        "SELECT user_id FROM users WHERE email = %s",
        (acc["email"],)
    )

    existing_user = cur.fetchone()

    if existing_user:
        print(
            f"  Skipped (already exists): "
            f"{acc['email']} ({acc['role']} - {acc['name']})"
        )
        continue

    # Create bcrypt password hash
    hashed = make_hash(acc["plain_password"])

    try:

        cur.execute(
            """
            INSERT INTO users
                (email, password_hash, role, linked_id)
            VALUES
                (%s, %s, %s, %s)
            """,
            (
                acc["email"],
                hashed,
                acc["role"],
                acc["linked_id"]
            )
        )

        conn.commit()

        print(
            f"  Inserted: "
            f"{acc['email']} "
            f"({acc['role']} - {acc['name']})"
        )

    except mysql.connector.Error as exc:

        conn.rollback()

        print(
            f"  ERROR inserting {acc['email']}: {exc}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Close connection
# ─────────────────────────────────────────────────────────────────────────────

cur.close()
conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────────────────────────────────────

print()
print("Seed complete.")
print()

print("Doctor login:  doctor1@caresync.local  /  Doctor@1234")
print("Doctor login:  doctor2@caresync.local  /  Doctor@1234")
print("Patient login: patient1@caresync.local /  Patient@1234")
print("Patient login: patient2@caresync.local /  Patient@1234")