# ============================================================
# generate_data.py
# CareSync Sample Data Generator
# ============================================================

# Install required libraries:
# pip install mysql-connector-python
# pip install Faker

import mysql.connector
import random
from faker import Faker
from datetime import date, timedelta, datetime


# ============================================================
# FAKER
# ============================================================

fake = Faker('en_IN')


# ============================================================
# DATABASE CONNECTION
# ============================================================

connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='',
    database='caresync'
)

cursor = connection.cursor()

print("Connected to MySQL successfully.")


# ============================================================
# CONSTANTS
# ============================================================

NUM_DOCTORS = 40
NUM_PATIENTS = 500
NUM_APPOINTMENTS = 3000
NUM_MEDICAL_RECORDS = 2000
NUM_BILLS = 2500
NUM_ACTIVITY_LOGS = 1000

NUM_ADMINS = 2
NUM_BILLING_STAFF = 10


# ============================================================
# MASTER DATA
# ============================================================

SPECIALIZATIONS = [
    'Cardiology',
    'General Medicine',
    'Orthopaedics',
    'Gynaecology',
    'Paediatrics',
    'Neurology',
    'Dermatology',
    'Ophthalmology',
    'ENT',
    'Psychiatry',
    'Oncology',
    'Urology',
    'Endocrinology'
]


BLOOD_GROUPS = [
    'A+', 'A-', 'B+', 'B-',
    'O+', 'O-', 'AB+', 'AB-'
]


DIAGNOSES = [
    'Hypertension',
    'Type 2 Diabetes',
    'Upper Respiratory Infection',
    'Migraine',
    'Lumbar Spondylosis',
    'Anxiety Disorder',
    'Anaemia',
    'Hypothyroidism',
    'Gastritis',
    'Urinary Tract Infection',
    'Dengue Fever',
    'Viral Fever',
    'Asthma',
    'Arthritis',
    'Obesity',
    'Iron Deficiency',
    'Vitamin D Deficiency',
    'Sinusitis',
    'Eczema'
]


TESTS = [
    'CBC',
    'Blood Sugar',
    'Lipid Profile',
    'Liver Function Test',
    'Kidney Function Test',
    'Thyroid Test',
    'Urine Test',
    'X-Ray',
    'MRI',
    'CT Scan',
    'ECG',
    'Vitamin D Test'
]


INSURANCE_PROVIDERS = [
    'Star Health Insurance',
    'HDFC ERGO',
    'ICICI Lombard',
    'Bajaj Allianz',
    'Care Health Insurance',
    'Niva Bupa',
    'Aditya Birla Health Insurance'
]


REJECTION_REASONS = [
    'Insurance claim limit exceeded.',
    'Procedure not covered under insurance plan.',
    'Pre-authorisation was not obtained.',
    'Patient not eligible under submitted policy.',
    'Duplicate claim submitted.',
    'Medical documents are incomplete.',
    'Claim submitted after deadline.'
]


ACTIONS = [
    'Login',
    'Logout',
    'View Profile',
    'Book Appointment',
    'Cancel Appointment',
    'View Appointment',
    'View Medical Record',
    'Add Medical Record',
    'Update Medical Record',
    'View Billing',
    'View Claim',
    'Upload Report',
    'View Report'
]


TARGET_TABLES = [
    'patient',
    'doctor',
    'appointment',
    'medical_record',
    'billing'
]


# ============================================================
# DEFAULT PASSWORD
# ============================================================

DEFAULT_PASSWORD = "CareSync@123"


# ============================================================
# HELPER FUNCTION - PHONE NUMBER
# ============================================================

def generate_phone():
    return '9' + str(random.randint(100000000, 999999999))


# ============================================================
# STEP 1: INSERT ADMINS
# ============================================================

print()
print(f"Inserting {NUM_ADMINS} admins...")

admin_ids = []

for i in range(NUM_ADMINS):

    name = fake.name()
    email = f"admin{i + 1}@caresync.in"
    contact = generate_phone()
    role = "Administrator"

    cursor.execute(
        """
        INSERT INTO admin
        (name, email, password_hash, contact, role)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            name,
            email,
            DEFAULT_PASSWORD,
            contact,
            role
        )
    )

    admin_ids.append(cursor.lastrowid)


connection.commit()

print(f"Done. Inserted {len(admin_ids)} admins.")


# ============================================================
# STEP 2: INSERT BILLING STAFF
# ============================================================

print()
print(f"Inserting {NUM_BILLING_STAFF} billing staff...")

billing_staff_ids = []

for i in range(NUM_BILLING_STAFF):

    name = fake.name()
    contact = generate_phone()
    email = f"billing{i + 1}@caresync.in"
    is_active = 1
    department = "Billing Department"

    cursor.execute(
        """
        INSERT INTO billing_staff
        (name, contact, email, password_hash, is_active, department)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            name,
            contact,
            email,
            DEFAULT_PASSWORD,
            is_active,
            department
        )
    )

    billing_staff_ids.append(cursor.lastrowid)


connection.commit()

print(f"Done. Inserted {len(billing_staff_ids)} billing staff.")


# ============================================================
# STEP 3: INSERT DOCTORS
# ============================================================

print()
print(f"Inserting {NUM_DOCTORS} doctors...")

doctor_ids = []

for i in range(NUM_DOCTORS):

    name = "Dr. " + fake.name()
    specialization = random.choice(SPECIALIZATIONS)
    contact = generate_phone()
    email = f"doctor{i + 1}@caresync.in"
    is_active = 1

    cursor.execute(
        """
        INSERT INTO doctor
        (name, specialization, contact, email, password_hash, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            name,
            specialization,
            contact,
            email,
            DEFAULT_PASSWORD,
            is_active
        )
    )

    doctor_ids.append(cursor.lastrowid)


connection.commit()

print(f"Done. Inserted {len(doctor_ids)} doctors.")


# ============================================================
# STEP 4: INSERT PATIENTS
# ============================================================

print()
print(f"Inserting {NUM_PATIENTS} patients...")

patient_ids = []

for i in range(NUM_PATIENTS):

    name = fake.name()

    email = f"patient{i + 1}@caresync.in"

    password = DEFAULT_PASSWORD

    dob = fake.date_of_birth(
        minimum_age=5,
        maximum_age=85
    )

    contact = generate_phone()

    address = fake.address().replace(
        '\n',
        ', '
    )

    blood_group = random.choice(
        BLOOD_GROUPS
    )

    cursor.execute(
        """
        INSERT INTO patient
        (
            name,
            email,
            password_hash,
            date_of_birth,
            contact,
            address,
            blood_group
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            name,
            email,
            password,
            dob,
            contact,
            address,
            blood_group
        )
    )

    patient_ids.append(
        cursor.lastrowid
    )


connection.commit()

print(f"Done. Inserted {len(patient_ids)} patients.")


# ============================================================
# STEP 5: INSERT APPOINTMENTS
# ============================================================

print()
print(f"Inserting {NUM_APPOINTMENTS} appointments...")

appointment_ids = []

start_date = date.today() - timedelta(days=730)

for _ in range(NUM_APPOINTMENTS):

    patient_id = random.choice(patient_ids)

    doctor_id = random.choice(doctor_ids)

    random_date = start_date + timedelta(
        days=random.randint(0, 730)
    )

    hour = random.randint(9, 16)

    minute = random.choice(
        [0, 15, 30, 45]
    )

    appointment_datetime = datetime(
        random_date.year,
        random_date.month,
        random_date.day,
        hour,
        minute
    )

    diagnosis = random.choice(
        DIAGNOSES
    )

    reason = (
        "Patient complaints of "
        + diagnosis.lower()
    )

    status = random.choices(
        [
            'Completed',
            'Scheduled',
            'Cancelled'
        ],
        weights=[
            80,
            10,
            10
        ]
    )[0]

    cursor.execute(
        """
        INSERT INTO appointment
        (
            patient_id,
            doctor_id,
            date_and_time,
            reason,
            status
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            patient_id,
            doctor_id,
            appointment_datetime,
            reason,
            status
        )
    )

    appointment_ids.append(
        cursor.lastrowid
    )


connection.commit()

print(
    f"Done. Inserted "
    f"{len(appointment_ids)} appointments."
)


# ============================================================
# STEP 6: INSERT MEDICAL RECORDS
# ============================================================

print()
print(
    f"Inserting {NUM_MEDICAL_RECORDS} "
    "medical records..."
)

medical_record_ids = []

for _ in range(NUM_MEDICAL_RECORDS):

    patient_id = random.choice(
        patient_ids
    )

    doctor_id = random.choice(
        doctor_ids
    )

    diagnosis = random.choice(
        DIAGNOSES
    )

    medical_history = (
        "Patient has a history related to "
        + diagnosis
        + "."
    )

    prescription = (
        "Prescribed medication for "
        + diagnosis
        + "."
    )

    test_name = random.choice(
        TESTS
    )

    test_result = random.choice(
        [
            "Normal",
            "Mildly elevated",
            "Within normal range",
            "Requires follow-up",
            "Abnormal"
        ]
    )

    cursor.execute(
        """
        INSERT INTO medical_record
        (
            patient_id,
            doctor_id,
            medical_history,
            diagnosis,
            prescription,
            test_name,
            test_result
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            patient_id,
            doctor_id,
            medical_history,
            diagnosis,
            prescription,
            test_name,
            test_result
        )
    )

    medical_record_ids.append(
        cursor.lastrowid
    )


connection.commit()

print(
    f"Done. Inserted "
    f"{len(medical_record_ids)} medical records."
)


# ============================================================
# STEP 7: INSERT BILLING RECORDS
# ============================================================

print()
print(f"Inserting {NUM_BILLS} billing records...")

billing_ids = []

for _ in range(NUM_BILLS):

    patient_id = random.choice(
        patient_ids
    )

    total_amount = round(
        random.uniform(500, 50000),
        2
    )

    insurance_provider = random.choice(
        INSURANCE_PROVIDERS
    )

    claim_amount = round(
        total_amount * random.uniform(
            0.50,
            1.00
        ),
        2
    )

    claim_status = random.choices(
        [
            'Approved',
            'Pending',
            'Rejected'
        ],
        weights=[
            75,
            15,
            10
        ]
    )[0]

    if claim_status == 'Rejected':

        rejection_reason = random.choice(
            REJECTION_REASONS
        )

    else:

        rejection_reason = None

    cursor.execute(
        """
        INSERT INTO billing
        (
            patient_id,
            total_amount,
            insurance_provider,
            claim_amount,
            claim_status,
            rejection_reason
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            patient_id,
            total_amount,
            insurance_provider,
            claim_amount,
            claim_status,
            rejection_reason
        )
    )

    billing_ids.append(
        cursor.lastrowid
    )


connection.commit()

print(
    f"Done. Inserted "
    f"{len(billing_ids)} billing records."
)


# ============================================================
# STEP 8: INSERT ACTIVITY LOGS
# ============================================================

print()
print(
    f"Inserting {NUM_ACTIVITY_LOGS} "
    "activity logs..."
)

user_types = [
    'Patient',
    'Doctor',
    'Admin',
    'Billing Staff'
]


for _ in range(NUM_ACTIVITY_LOGS):

    user_type = random.choice(
        user_types
    )

    # Select an ID according to the user type
    if user_type == 'Patient':

        user_id = random.choice(
            patient_ids
        )

    elif user_type == 'Doctor':

        user_id = random.choice(
            doctor_ids
        )

    elif user_type == 'Admin':

        user_id = random.choice(
            admin_ids
        )

    else:

        user_id = random.choice(
            billing_staff_ids
        )


    action = random.choice(
        ACTIONS
    )

    target_table = random.choice(
        TARGET_TABLES
    )

    target_id = random.randint(
        1,
        100
    )

    logged_at = fake.date_time_between(
        start_date='-2y',
        end_date='now'
    )

    cursor.execute(
        """
        INSERT INTO activity_log
        (
            user_type,
            user_id,
            action,
            target_table,
            target_id,
            logged_at
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            user_type,
            user_id,
            action,
            target_table,
            target_id,
            logged_at
        )
    )


connection.commit()

print(
    f"Done. Inserted "
    f"{NUM_ACTIVITY_LOGS} activity logs."
)


# ============================================================
# FINAL ROW COUNTS
# ============================================================

print()
print("============================================")
print("        CARESYNC FINAL ROW COUNTS")
print("============================================")

tables = [
    'patient',
    'doctor',
    'admin',
    'billing_staff',
    'appointment',
    'medical_record',
    'billing',
    'activity_log'
]


for table in tables:

    cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    count = cursor.fetchone()[0]

    print(
        f"{table:20s}: {count}"
    )


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print()
print("============================================")
print("CareSync sample data generation completed.")
print("Database is ready for use.")
print("============================================")