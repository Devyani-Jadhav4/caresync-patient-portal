# day7_demo_seed_final.py
# Inserts demo appointments and billing records relative to TODAY.
#
# Past appointments are Completed.
# Future appointments are Scheduled.
# Billing records use the current CareSync billing table structure.
#
# Run:
#     python day7_demo_seed_final.py


import mysql.connector
from datetime import date, datetime, time, timedelta


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE CONNECTION
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
# GET DOCTOR 1 LINKED ID
# ─────────────────────────────────────────────────────────────────────────────

cur.execute("""
    SELECT linked_id
    FROM users
    WHERE email = 'doctor1@caresync.local'
      AND role = 'doctor'
    LIMIT 1
""")

row = cur.fetchone()

if not row:
    print(
        "ERROR: doctor1@caresync.local not found. "
        "Run day7_users_seed.py first."
    )
    cur.close()
    conn.close()
    exit()

DOCTOR_ID = row["linked_id"]


# ─────────────────────────────────────────────────────────────────────────────
# GET PATIENT 1 LINKED ID
# ─────────────────────────────────────────────────────────────────────────────

cur.execute("""
    SELECT linked_id
    FROM users
    WHERE email = 'patient1@caresync.local'
      AND role = 'patient'
    LIMIT 1
""")

row = cur.fetchone()

if not row:
    print(
        "ERROR: patient1@caresync.local not found. "
        "Run day7_users_seed.py first."
    )
    cur.close()
    conn.close()
    exit()

PATIENT_ID = row["linked_id"]


print(f"Doctor ID  : {DOCTOR_ID}")
print(f"Patient ID : {PATIENT_ID}")


# ─────────────────────────────────────────────────────────────────────────────
# DATES RELATIVE TO TODAY
# ─────────────────────────────────────────────────────────────────────────────

TODAY = date.today()

MINUS_7 = TODAY - timedelta(days=7)
MINUS_3 = TODAY - timedelta(days=3)
MINUS_1 = TODAY - timedelta(days=1)

PLUS_1 = TODAY + timedelta(days=1)
PLUS_3 = TODAY + timedelta(days=3)
PLUS_7 = TODAY + timedelta(days=7)


print(f"Today       : {TODAY}")
print(f"Past dates  : {MINUS_7}, {MINUS_3}, {MINUS_1}")
print(f"Future dates: {PLUS_1}, {PLUS_3}, {PLUS_7}")


# ─────────────────────────────────────────────────────────────────────────────
# CREATE DATETIME VALUES
#
# Your appointment table uses ONE column:
# date_and_time
# ─────────────────────────────────────────────────────────────────────────────

appointments = [

    # ── Past appointments ────────────────────────────────────────────────────

    {
        "patient_id": PATIENT_ID,
        "doctor_id": DOCTOR_ID,
        "date_and_time": datetime.combine(
            MINUS_7,
            time(9, 30)
        ),
        "status": "Completed",
        "reason": "Annual physical examination"
    },

    {
        "patient_id": PATIENT_ID,
        "doctor_id": DOCTOR_ID,
        "date_and_time": datetime.combine(
            MINUS_3,
            time(10, 0)
        ),
        "status": "Completed",
        "reason": "Follow-up after blood test"
    },

    {
        "patient_id": PATIENT_ID,
        "doctor_id": DOCTOR_ID,
        "date_and_time": datetime.combine(
            MINUS_1,
            time(11, 0)
        ),
        "status": "Completed",
        "reason": "Fever and fatigue"
    },

    # ── Future appointments ──────────────────────────────────────────────────

    {
        "patient_id": PATIENT_ID,
        "doctor_id": DOCTOR_ID,
        "date_and_time": datetime.combine(
            PLUS_1,
            time(9, 0)
        ),
        "status": "Scheduled",
        "reason": "Routine check-up"
    },

    {
        "patient_id": PATIENT_ID,
        "doctor_id": DOCTOR_ID,
        "date_and_time": datetime.combine(
            PLUS_3,
            time(10, 30)
        ),
        "status": "Scheduled",
        "reason": "Diabetes management review"
    },

    {
        "patient_id": PATIENT_ID,
        "doctor_id": DOCTOR_ID,
        "date_and_time": datetime.combine(
            PLUS_7,
            time(11, 0)
        ),
        "status": "Scheduled",
        "reason": "Post-surgery follow-up"
    }
]


# ─────────────────────────────────────────────────────────────────────────────
# INSERT APPOINTMENTS
# ─────────────────────────────────────────────────────────────────────────────

print()
print("Inserting appointments...")

inserted_ids = []


for appt in appointments:

    cur.execute("""
        INSERT INTO appointment
            (
                patient_id,
                doctor_id,
                date_and_time,
                reason,
                status
            )
        VALUES
            (%s, %s, %s, %s, %s)
    """, (
        appt["patient_id"],
        appt["doctor_id"],
        appt["date_and_time"],
        appt["reason"],
        appt["status"]
    ))

    conn.commit()

    new_id = cur.lastrowid

    inserted_ids.append({
        "id": new_id,
        "status": appt["status"],
        "date_and_time": appt["date_and_time"]
    })

    print(
        f"  ID {new_id} | "
        f"{appt['date_and_time']} | "
        f"{appt['status']} | "
        f"{appt['reason']}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# BILLING RECORDS
#
# IMPORTANT:
# Current billing table does NOT contain:
#     appointment_id
#     bill_date
#     amount_paid
#     discount
#     status
#
# It contains:
#     patient_id
#     total_amount
#     insurance_provider
#     claim_amount
#     claim_status
#     rejection_reason
# ─────────────────────────────────────────────────────────────────────────────

print()
print("Inserting billing records...")


billing_records = [

    # Past completed appointment
    {
        "patient_id": PATIENT_ID,
        "total_amount": 1500.00,
        "insurance_provider": "HealthCare Insurance",
        "claim_amount": 1500.00,
        "claim_status": "Approved",
        "rejection_reason": None
    },

    # Past completed appointment
    {
        "patient_id": PATIENT_ID,
        "total_amount": 2200.00,
        "insurance_provider": "HealthCare Insurance",
        "claim_amount": 1000.00,
        "claim_status": "Pending",
        "rejection_reason": None
    },

    # Past completed appointment
    {
        "patient_id": PATIENT_ID,
        "total_amount": 800.00,
        "insurance_provider": "HealthCare Insurance",
        "claim_amount": 800.00,
        "claim_status": "Approved",
        "rejection_reason": None
    },

    # Future scheduled appointment
    {
        "patient_id": PATIENT_ID,
        "total_amount": 1200.00,
        "insurance_provider": "HealthCare Insurance",
        "claim_amount": 0.00,
        "claim_status": "Pending",
        "rejection_reason": None
    },

    # Future scheduled appointment
    {
        "patient_id": PATIENT_ID,
        "total_amount": 3500.00,
        "insurance_provider": "HealthCare Insurance",
        "claim_amount": 500.00,
        "claim_status": "Pending",
        "rejection_reason": None
    },

    # Future scheduled appointment
    {
        "patient_id": PATIENT_ID,
        "total_amount": 1800.00,
        "insurance_provider": "HealthCare Insurance",
        "claim_amount": 0.00,
        "claim_status": "Pending",
        "rejection_reason": None
    }
]


# ─────────────────────────────────────────────────────────────────────────────
# INSERT BILLING
# ─────────────────────────────────────────────────────────────────────────────

for bill in billing_records:

    cur.execute("""
        INSERT INTO billing
            (
                patient_id,
                total_amount,
                insurance_provider,
                claim_amount,
                claim_status,
                rejection_reason
            )
        VALUES
            (%s, %s, %s, %s, %s, %s)
    """, (
        bill["patient_id"],
        bill["total_amount"],
        bill["insurance_provider"],
        bill["claim_amount"],
        bill["claim_status"],
        bill["rejection_reason"]
    ))

    conn.commit()

    print(
        f"  Bill ID {cur.lastrowid} | "
        f"Rs {bill['total_amount']:.2f} | "
        f"Claim: Rs {bill['claim_amount']:.2f} | "
        f"{bill['claim_status']}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLOSE CONNECTION
# ─────────────────────────────────────────────────────────────────────────────

cur.close()
conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# COMPLETE
# ─────────────────────────────────────────────────────────────────────────────

print()
print("Demo data inserted successfully.")
print()

print(
    "Doctor dashboard : "
    "doctor1@caresync.local / Doctor@1234"
)

print(
    "                    Shows past and upcoming appointments."
)

print()

print(
    "Patient dashboard: "
    "patient1@caresync.local / Patient@1234"
)

print(
    "                    Shows appointments and billing records."
)