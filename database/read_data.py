```python
# read_data.py
# CareSync Database Reader
#
# This script connects Python to MySQL and runs
# meaningful queries on the CareSync database.
#
# FINAL ENTITIES:
# 1. Patient
# 2. Doctor
# 3. Admin
# 4. Billing Staff
# 5. Appointment
# 6. Medical Record
# 7. Billing
# 8. Activity Log
#
# Required library:
# pip install mysql-connector-python


import mysql.connector


# ============================================================
# DATABASE CONNECTION
# ============================================================

connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="CareSync@2024",
    database="caresync"
)

cursor = connection.cursor(dictionary=True)

print("Connected to CareSync database.")
print("=" * 65)


# ============================================================
# QUERY 1
# DOCTOR COUNT BY SPECIALIZATION
# ============================================================

print()
print("QUERY 1: Doctor Count by Specialization")
print("-" * 50)


cursor.execute(
    """
    SELECT
        specialization,
        COUNT(*) AS total_doctors
    FROM doctor
    WHERE is_active = 1
    GROUP BY specialization
    ORDER BY total_doctors DESC
    """
)


rows = cursor.fetchall()


if not rows:

    print("No active doctors found.")

else:

    for row in rows:

        print(
            f"  {row['specialization']:<25}"
            f" {row['total_doctors']} doctors"
        )


# ============================================================
# QUERY 2
# BILLING SUMMARY BY CLAIM STATUS
# ============================================================

print()
print("QUERY 2: Billing Summary by Claim Status")
print("-" * 50)


cursor.execute(
    """
    SELECT
        claim_status,
        COUNT(*) AS total_bills,
        ROUND(SUM(total_amount), 2) AS total_billed,
        ROUND(SUM(COALESCE(claim_amount, 0)), 2) AS total_claim_amount,
        ROUND(AVG(total_amount), 2) AS average_bill_amount
    FROM billing
    GROUP BY claim_status
    ORDER BY total_billed DESC
    """
)


rows = cursor.fetchall()


if not rows:

    print("No billing records found.")

else:

    for row in rows:

        print(
            f"  {row['claim_status']:<12}"
            f" Bills: {row['total_bills']:>5}"
            f"  Billed: Rs {row['total_billed']:>10.2f}"
            f"  Claims: Rs {row['total_claim_amount']:>10.2f}"
        )


# ============================================================
# QUERY 3
# BILL REJECTION RATE
# ============================================================

print()
print("QUERY 3: Bill Rejection Rate")
print("-" * 50)


cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM billing
    """
)


total_bills = cursor.fetchone()["total"]


cursor.execute(
    """
    SELECT COUNT(*) AS rejected
    FROM billing
    WHERE claim_status = 'Rejected'
    """
)


rejected_bills = cursor.fetchone()["rejected"]


if total_bills > 0:

    rejection_rate = (
        rejected_bills / total_bills
    ) * 100

else:

    rejection_rate = 0


print(f"  Total Bills    : {total_bills}")
print(f"  Rejected Bills : {rejected_bills}")
print(f"  Rejection Rate : {rejection_rate:.2f}%")


# ============================================================
# QUERY 4
# TOP 5 BUSIEST DOCTORS
# ============================================================

print()
print("QUERY 4: Top 5 Busiest Doctors")
print("-" * 55)


cursor.execute(
    """
    SELECT
        d.name,
        d.specialization,
        COUNT(a.appointment_id) AS total_appointments
    FROM doctor d
    JOIN appointment a
        ON a.doctor_id = d.doctor_id
    WHERE a.status = 'Completed'
    GROUP BY
        d.doctor_id,
        d.name,
        d.specialization
    ORDER BY total_appointments DESC
    LIMIT 5
    """
)


rows = cursor.fetchall()


if not rows:

    print("No completed appointments found.")

else:

    for i, row in enumerate(rows, start=1):

        print(
            f"  {i}. {row['name']:<30}"
            f" ({row['specialization']:<20})"
            f" {row['total_appointments']} completed appointments"
        )


# ============================================================
# QUERY 5
# PATIENTS WITH MORE THAN 5 COMPLETED VISITS
# ============================================================

print()
print("QUERY 5: Patients With More Than 5 Completed Visits")
print("-" * 60)


cursor.execute(
    """
    SELECT
        p.name,
        p.blood_group,
        COUNT(a.appointment_id) AS visit_count
    FROM patient p
    JOIN appointment a
        ON a.patient_id = p.patient_id
    WHERE a.status = 'Completed'
    GROUP BY
        p.patient_id,
        p.name,
        p.blood_group
    HAVING visit_count > 5
    ORDER BY visit_count DESC
    LIMIT 10
    """
)


rows = cursor.fetchall()


if not rows:

    print("  No patients with more than 5 completed visits found.")

else:

    for row in rows:

        print(
            f"  {row['name']:<30}"
            f" Blood: {row['blood_group']:<4}"
            f" Visits: {row['visit_count']}"
        )


# ============================================================
# QUERY 6
# MONTHLY APPOINTMENT TREND - LAST 6 MONTHS
# ============================================================

print()
print("QUERY 6: Monthly Appointment Count - Last 6 Months")
print("-" * 60)


cursor.execute(
    """
    SELECT
        DATE_FORMAT(date_and_time, '%Y-%m') AS month,
        COUNT(*) AS total_appointments
    FROM appointment
    WHERE date_and_time >=
          DATE_SUB(NOW(), INTERVAL 6 MONTH)
    GROUP BY month
    ORDER BY month ASC
    """
)


rows = cursor.fetchall()


if not rows:

    print("  No appointments found in the last 6 months.")

else:

    for row in rows:

        print(
            f"  {row['month']}"
            f"   {row['total_appointments']} appointments"
        )


# ============================================================
# QUERY 7
# APPOINTMENT STATUS SUMMARY
# ============================================================

print()
print("QUERY 7: Appointment Status Summary")
print("-" * 50)


cursor.execute(
    """
    SELECT
        status,
        COUNT(*) AS total_appointments
    FROM appointment
    GROUP BY status
    ORDER BY total_appointments DESC
    """
)


rows = cursor.fetchall()


if not rows:

    print("No appointment records found.")

else:

    for row in rows:

        print(
            f"  {row['status']:<12}"
            f" {row['total_appointments']} appointments"
        )


# ============================================================
# QUERY 8
# ACTIVE VS INACTIVE DOCTORS
# ============================================================

print()
print("QUERY 8: Doctor Active Status")
print("-" * 50)


cursor.execute(
    """
    SELECT
        CASE
            WHEN is_active = 1 THEN 'Active'
            ELSE 'Inactive'
        END AS doctor_status,
        COUNT(*) AS total_doctors
    FROM doctor
    GROUP BY is_active
    ORDER BY is_active DESC
    """
)


rows = cursor.fetchall()


for row in rows:

    print(
        f"  {row['doctor_status']:<10}"
        f" {row['total_doctors']} doctors"
    )


# ============================================================
# QUERY 9
# MEDICAL RECORD COUNT BY DOCTOR
# ============================================================

print()
print("QUERY 9: Medical Records by Doctor")
print("-" * 55)


cursor.execute(
    """
    SELECT
        d.name,
        d.specialization,
        COUNT(m.medical_record_id) AS total_records
    FROM doctor d
    JOIN medical_record m
        ON m.doctor_id = d.doctor_id
    GROUP BY
        d.doctor_id,
        d.name,
        d.specialization
    ORDER BY total_records DESC
    LIMIT 10
    """
)


rows = cursor.fetchall()


if not rows:

    print("No medical records found.")

else:

    for row in rows:

        print(
            f"  {row['name']:<30}"
            f" ({row['specialization']:<20})"
            f" Records: {row['total_records']}"
        )


# ============================================================
# QUERY 10
# INSURANCE CLAIM STATUS SUMMARY
# ============================================================

print()
print("QUERY 10: Insurance Claim Status Summary")
print("-" * 55)


cursor.execute(
    """
    SELECT
        claim_status,
        COUNT(*) AS total_claims,
        ROUND(SUM(claim_amount), 2) AS total_claim_amount
    FROM billing
    GROUP BY claim_status
    ORDER BY total_claims DESC
    """
)


rows = cursor.fetchall()


if not rows:

    print("No insurance claims found.")

else:

    for row in rows:

        total_claim_amount = row["total_claim_amount"] or 0

        print(
            f"  {row['claim_status']:<12}"
            f" Claims: {row['total_claims']:>5}"
            f"  Amount: Rs {total_claim_amount:>12.2f}"
        )


# ============================================================
# QUERY 11
# ACTIVITY LOG SUMMARY BY USER TYPE
# ============================================================

print()
print("QUERY 11: Activity Count by User Type")
print("-" * 50)


cursor.execute(
    """
    SELECT
        user_type,
        COUNT(*) AS total_activities
    FROM activity_log
    GROUP BY user_type
    ORDER BY total_activities DESC
    """
)


rows = cursor.fetchall()


if not rows:

    print("No activity logs found.")

else:

    for row in rows:

        print(
            f"  {row['user_type']:<15}"
            f" {row['total_activities']} activities"
        )


# ============================================================
# QUERY 12
# MOST COMMON ACTIVITY ACTIONS
# ============================================================

print()
print("QUERY 12: Most Common Activity Actions")
print("-" * 50)


cursor.execute(
    """
    SELECT
        action,
        COUNT(*) AS action_count
    FROM activity_log
    GROUP BY action
    ORDER BY action_count DESC
    LIMIT 10
    """
)


rows = cursor.fetchall()


if not rows:

    print("No activity actions found.")

else:

    for row in rows:

        print(
            f"  {row['action']:<25}"
            f" {row['action_count']} times"
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 65)
print("DATABASE SUMMARY")
print("=" * 65)


summary_tables = [
    "patient",
    "doctor",
    "admin",
    "billing_staff",
    "appointment",
    "medical_record",
    "billing",
    "activity_log"
]


for table in summary_tables:

    cursor.execute(
        f"SELECT COUNT(*) AS total FROM {table}"
    )

    count = cursor.fetchone()["total"]

    print(
        f"  {table:<20}: {count} rows"
    )


# ============================================================
# CLEANUP
# ============================================================

cursor.close()

connection.close()


print()
print("=" * 65)
print("All queries completed successfully.")
print("Database connection closed.")
print("=" * 65)