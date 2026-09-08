# generate_data.py
# CareSync Sample Data Generator
#
# This script populates the CareSync database with realistic test data.
# Run this after creating your database and tables.
#
# Required libraries:
#   pip install mysql-connector-python
#   pip install Faker

import mysql.connector
import random
from faker import Faker
from datetime import date, timedelta, datetime, time

# Create Faker instance using Indian-style data
fake = Faker('en_IN')


# ─── DATABASE CONNECTION ────────────────────────────────────────────────────

connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='',
    database='caresync'
)

cursor = connection.cursor()

print('Connected to MySQL successfully.')


# ─── CONSTANTS ──────────────────────────────────────────────────────────────

NUM_DOCTORS = 40
NUM_PATIENTS = 500
NUM_APPOINTMENTS = 3000
NUM_BILLS = 2500

BILL_REJECT_LOW = 0.08
BILL_REJECT_HIGH = 0.12


SPECIALISATIONS = [
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


REJECTION_REASONS = [
    'Insurance claim limit exceeded for this policy year.',
    'Procedure not covered under current insurance plan.',
    'Pre-authorisation was not obtained before treatment.',
    'Patient not eligible under submitted insurance policy.',
    'Duplicate claim submitted for the same service date.',
    'Medical documents submitted are incomplete.',
    'Claim submitted after the deadline specified by insurer.'
]


INSURANCE_PROVIDERS = [
    'Star Health Insurance',
    'HDFC ERGO',
    'ICICI Lombard',
    'Niva Bupa',
    'Care Health Insurance',
    'Aditya Birla Health Insurance'
]


# ─── STEP 0: CLEAR OLD GENERATED DATA ───────────────────────────────────────

print()
print('Clearing previous generated data...')

# Delete child/dependent tables first.
# Foreign keys are temporarily disabled so the tables can be cleared safely.

cursor.execute('SET FOREIGN_KEY_CHECKS = 0')

cursor.execute('TRUNCATE TABLE activity_log')
cursor.execute('TRUNCATE TABLE billing')
cursor.execute('TRUNCATE TABLE medical_record')
cursor.execute('TRUNCATE TABLE appointment')
cursor.execute('TRUNCATE TABLE billing_staff')
cursor.execute('TRUNCATE TABLE admin')
cursor.execute('TRUNCATE TABLE doctor')
cursor.execute('TRUNCATE TABLE patient')

cursor.execute('SET FOREIGN_KEY_CHECKS = 1')

connection.commit()

print('  Previous generated data cleared.')


# ─── STEP 1: INSERT DOCTORS ─────────────────────────────────────────────────

print()
print(f'Inserting {NUM_DOCTORS} doctors...')

doctor_ids = []

for i in range(NUM_DOCTORS):

    name = 'Dr. ' + fake.name()

    specialization = random.choice(SPECIALISATIONS)

    contact = '9' + str(
        random.randint(100000000, 999999999)
    )

    email = f'doctor{i + 1}@caresync.in'

    password_hash = 'password123'

    is_active = 1

    cursor.execute(
        '''
        INSERT INTO doctor
            (name, specialization, contact, email, password_hash, is_active)
        VALUES
            (%s, %s, %s, %s, %s, %s)
        ''',
        (
            name,
            specialization,
            contact,
            email,
            password_hash,
            is_active
        )
    )

    doctor_ids.append(cursor.lastrowid)

connection.commit()

print(f'  Done. Inserted {len(doctor_ids)} doctors.')


# ─── STEP 2: INSERT PATIENTS ────────────────────────────────────────────────

print()
print(f'Inserting {NUM_PATIENTS} patients...')

patient_ids = []

for i in range(NUM_PATIENTS):

    name = fake.name()

    dob = fake.date_of_birth(
        minimum_age=5,
        maximum_age=85
    )

    contact = '9' + str(
        random.randint(100000000, 999999999)
    )

    email = f'patient{i + 1}@caresync.in'

    address = fake.address().replace('\n', ', ')

    blood_group = random.choice(BLOOD_GROUPS)

    password_hash = 'password123'

    cursor.execute(
        '''
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
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (
            name,
            email,
            password_hash,
            dob,
            contact,
            address,
            blood_group
        )
    )

    patient_ids.append(cursor.lastrowid)

connection.commit()

print(f'  Done. Inserted {len(patient_ids)} patients.')


# ─── STEP 3: INSERT APPOINTMENTS ────────────────────────────────────────────

print()
print(f'Inserting {NUM_APPOINTMENTS} appointments...')

appointment_ids = []

start_date = date.today() - timedelta(days=730)
end_date = date.today()

hour_options = list(range(9, 17))
minute_options = [0, 15, 30, 45]


for _ in range(NUM_APPOINTMENTS):

    # Select random patient and doctor
    p_id = random.choice(patient_ids)
    d_id = random.choice(doctor_ids)

    # Generate random date
    appointment_date = start_date + timedelta(
        days=random.randint(
            0,
            (end_date - start_date).days
        )
    )

    # Generate random time
    appointment_time = time(
        hour=random.choice(hour_options),
        minute=random.choice(minute_options),
        second=0
    )

    # Combine date + time into DATETIME
    date_and_time = datetime.combine(
        appointment_date,
        appointment_time
    )

    reason = (
        'Patient complaints of '
        + random.choice(DIAGNOSES).lower()
    )

    # Weight:
    # 80% Completed
    # 10% Scheduled
    # 10% Cancelled

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
        '''
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
        ''',
        (
            p_id,
            d_id,
            date_and_time,
            reason,
            status
        )
    )

    appointment_ids.append(cursor.lastrowid)


connection.commit()

print(
    f'  Done. Inserted {len(appointment_ids)} appointments.'
)


# ─── STEP 4: INSERT MEDICAL RECORDS ─────────────────────────────────────────

print()
print('Inserting medical records...')

medical_record_count = 0

# Create medical records mainly for completed appointments

cursor.execute(
    '''
    SELECT appointment_id, patient_id, doctor_id
    FROM appointment
    WHERE status = 'Completed'
    '''
)

completed_appointments = cursor.fetchall()

for appointment in completed_appointments:

    appointment_id = appointment[0]
    patient_id = appointment[1]
    doctor_id = appointment[2]

    diagnosis = random.choice(DIAGNOSES)

    medical_history = random.choice([
        'No significant previous medical history.',
        'Previous history of seasonal allergies.',
        'History of hypertension.',
        'History of diabetes.',
        'Previous minor surgical procedure.',
        'Family history of cardiovascular disease.',
        'No known chronic medical condition.'
    ])

    prescription = random.choice([
        'Paracetamol 500mg as required.',
        'Continue prescribed medication for 5 days.',
        'Antibiotic course for 5 days.',
        'Daily vitamin supplementation.',
        'Medication as advised by doctor.'
    ])

    test_name = random.choice([
        'Complete Blood Count',
        'Blood Sugar Test',
        'Lipid Profile',
        'Liver Function Test',
        'Kidney Function Test',
        'Thyroid Function Test',
        'Vitamin D Test'
    ])

    test_result = random.choice([
        'Results within normal range.',
        'Mildly elevated values observed.',
        'Values require routine monitoring.',
        'Results suggest follow-up consultation.',
        'No significant abnormality detected.'
    ])

    cursor.execute(
        '''
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
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        ''',
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

    medical_record_count += 1


connection.commit()

print(
    f'  Done. Inserted {medical_record_count} medical records.'
)


# ─── STEP 5: INSERT BILLING RECORDS ─────────────────────────────────────────

print()
print(f'Inserting {NUM_BILLS} billing records...')


# Billing table in the current database contains:
#
# bill_id
# patient_id
# total_amount
# insurance_provider
# claim_amount
# claim_status
# rejection_reason
#
# It does NOT contain:
# appointment_id
# amount_paid
# discount
# status
# bill_date
# due_date


cursor.execute(
    '''
    SELECT appointment_id, patient_id
    FROM appointment
    WHERE status = 'Completed'
    '''
)

completed_appointments = cursor.fetchall()


if len(completed_appointments) < NUM_BILLS:

    print(
        f'  Only {len(completed_appointments)} completed appointments available.'
    )

    bills_to_create = completed_appointments

else:

    bills_to_create = random.sample(
        completed_appointments,
        NUM_BILLS
    )


reject_rate = random.uniform(
    BILL_REJECT_LOW,
    BILL_REJECT_HIGH
)

print(
    f'  Bill rejection rate: {reject_rate * 100:.1f}%'
)


bills_inserted = 0


for (appointment_id, patient_id) in bills_to_create:

    total_amount = round(
        random.uniform(300, 3000),
        2
    )

    insurance_provider = random.choice(
        INSURANCE_PROVIDERS
    )

    # Claim amount between 50% and 100% of total bill
    claim_amount = round(
        total_amount * random.uniform(0.50, 1.00),
        2
    )

    random_value = random.random()

    if random_value < reject_rate:

        claim_status = 'Rejected'

        rejection_reason = random.choice(
            REJECTION_REASONS
        )

    elif random_value < 0.60:

        claim_status = 'Pending'

        rejection_reason = None

    else:

        claim_status = 'Approved'

        rejection_reason = None


    cursor.execute(
        '''
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
        ''',
        (
            patient_id,
            total_amount,
            insurance_provider,
            claim_amount,
            claim_status,
            rejection_reason
        )
    )

    bills_inserted += 1


connection.commit()

print(
    f'  Done. Inserted {bills_inserted} billing records.'
)


# ─── STEP 6: INSERT ACTIVITY LOGS ────────────────────────────────────────────

print()
print('Inserting activity logs...')

activity_count = 0


# Patient activities

for patient_id in patient_ids[:100]:

    cursor.execute(
        '''
        INSERT INTO activity_log
            (
                user_type,
                user_id,
                action,
                target_table,
                target_id
            )
        VALUES
            (%s, %s, %s, %s, %s)
        ''',
        (
            'Patient',
            patient_id,
            'Login',
            None,
            None
        )
    )

    activity_count += 1


# Doctor activities

for doctor_id in doctor_ids:

    cursor.execute(
        '''
        INSERT INTO activity_log
            (
                user_type,
                user_id,
                action,
                target_table,
                target_id
            )
        VALUES
            (%s, %s, %s, %s, %s)
        ''',
        (
            'Doctor',
            doctor_id,
            'Login',
            None,
            None
        )
    )

    activity_count += 1


connection.commit()

print(
    f'  Done. Inserted {activity_count} activity logs.'
)


# ─── STEP 7: VERIFY ROW COUNTS ──────────────────────────────────────────────

print()
print('==========================================')
print('        FINAL DATABASE ROW COUNTS')
print('==========================================')

tables = [
    'doctor',
    'patient',
    'appointment',
    'medical_record',
    'billing',
    'activity_log'
]


for table in tables:

    cursor.execute(
        f'SELECT COUNT(*) FROM {table}'
    )

    count = cursor.fetchone()[0]

    print(
        f'  {table:20s}: {count} rows'
    )


# ─── CLEANUP ────────────────────────────────────────────────────────────────

cursor.close()
connection.close()

print()
print('==========================================')
print(' Database population completed successfully.')
print('==========================================')