"""
CareSync Dashboard Backend
FastAPI + MySQL

Run:
    uvicorn main:app --reload

Set your MySQL password before running:
Windows CMD:
    set MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
"""

import os
from decimal import Decimal

import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="CareSync Dashboard API", version="1.0.0")

# Development CORS configuration.
# For production, replace "*" with the exact frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_db():
    """Create a fresh MySQL connection for each API request."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "caresync"),
    )


def close_db(db, cursor):
    """Close cursor and connection safely."""
    try:
        if cursor:
            cursor.close()
    finally:
        if db:
            db.close()


@app.get("/summary")
def get_summary():
    """Return dashboard summary numbers using the actual CareSync schema."""
    db = cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM patient")
        patients = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM doctor WHERE is_active = 1")
        doctors = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM appointment")
        appointments = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM billing")
        bills = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM billing WHERE claim_status = 'Rejected'"
        )
        rejected = cursor.fetchone()["total"]

        rejection_rate = round((rejected / bills * 100), 1) if bills else 0

        cursor.execute(
            "SELECT COALESCE(ROUND(SUM(total_amount), 2), 0) AS total "
            "FROM billing"
        )
        revenue = cursor.fetchone()["total"] or 0

        return {
            "total_patients": patients,
            "total_doctors": doctors,
            "total_appointments": appointments,
            "total_bills": bills,
            "rejection_rate": rejection_rate,
            "total_revenue": float(revenue),
        }
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        close_db(db, cursor)


@app.get("/patients")
def get_patients():
    """Return the 50 most recently registered patients."""
    db = cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                patient_id,
                name,
                email,
                contact,
                blood_group,
                DATE_FORMAT(date_of_birth, '%d %b %Y') AS date_of_birth,
                DATE_FORMAT(created_at, '%d %b %Y') AS registered_on
            FROM patient
            ORDER BY created_at DESC
            LIMIT 50
            """
        )
        return {"patients": cursor.fetchall()}
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        close_db(db, cursor)


@app.get("/patients/{patient_id}")
def get_patient_by_id(patient_id: int):
    """Return one patient by ID. Invalid/non-existing ID returns 404."""
    db = cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                patient_id,
                name,
                email,
                contact,
                address,
                blood_group,
                DATE_FORMAT(date_of_birth, '%d %b %Y') AS date_of_birth,
                DATE_FORMAT(created_at, '%d %b %Y') AS registered_on
            FROM patient
            WHERE patient_id = %s
            """,
            (patient_id,),
        )
        patient = cursor.fetchone()

        if patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")

        return patient
    except HTTPException:
        raise
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        close_db(db, cursor)


@app.get("/patients/{patient_id}/appointments")
def get_patient_appointments(patient_id: int):
    """
    Return all appointments for one patient.
    An empty list is returned when the patient has no appointments.
    """
    db = cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.appointment_id,
                a.patient_id,
                a.doctor_id,
                d.name AS doctor_name,
                d.specialization,
                DATE_FORMAT(a.date_and_time, '%d %b %Y %H:%i') AS date_and_time,
                a.reason,
                a.status
            FROM appointment a
            JOIN patient p ON p.patient_id = a.patient_id
            JOIN doctor d ON d.doctor_id = a.doctor_id
            WHERE a.patient_id = %s
            ORDER BY a.date_and_time DESC
            """,
            (patient_id,),
        )
        return {"appointments": cursor.fetchall()}
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        close_db(db, cursor)


@app.get("/billing")
def get_billing():
    """Return 50 recent billing records using the actual billing schema."""
    db = cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                b.bill_id,
                p.name AS patient_name,
                b.total_amount,
                b.insurance_provider,
                b.claim_amount,
                b.claim_status,
                b.rejection_reason
            FROM billing b
            JOIN patient p ON p.patient_id = b.patient_id
            ORDER BY b.bill_id DESC
            LIMIT 50
            """
        )
        bills = cursor.fetchall()

        for bill in bills:
            if bill["total_amount"] is not None:
                bill["total_amount"] = float(bill["total_amount"])
            if bill["claim_amount"] is not None:
                bill["claim_amount"] = float(bill["claim_amount"])

        return {"bills": bills}
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        close_db(db, cursor)


@app.get("/doctors")
def get_doctors():
    """Return all active doctors and their completed appointment count."""
    db = cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                d.doctor_id,
                d.name,
                d.specialization,
                COUNT(a.appointment_id) AS total_appointments
            FROM doctor d
            LEFT JOIN appointment a
                ON a.doctor_id = d.doctor_id
                AND a.status = 'Completed'
            WHERE d.is_active = 1
            GROUP BY d.doctor_id, d.name, d.specialization
            ORDER BY total_appointments DESC
            """
        )
        return {"doctors": cursor.fetchall()}
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        close_db(db, cursor)


@app.get("/dashboard/blood-groups")
def get_blood_groups():
    """Return patient count by blood group for the dashboard chart."""
    db = cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                COALESCE(NULLIF(blood_group, ''), 'Unknown') AS blood_group,
                COUNT(*) AS total
            FROM patient
            GROUP BY COALESCE(NULLIF(blood_group, ''), 'Unknown')
            ORDER BY total DESC
            """
        )
        return {"data": cursor.fetchall()}
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        close_db(db, cursor)


@app.get("/dashboard/appointments-heatmap")
def get_appointments_heatmap():
    """
    Return appointment counts grouped by day of week and hour.
    The existing schema contains date_and_time, so this chart can be built
    without adding a new database column.
    """
    db = cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                DAYOFWEEK(date_and_time) AS day_number,
                HOUR(date_and_time) AS hour,
                COUNT(*) AS total
            FROM appointment
            GROUP BY DAYOFWEEK(date_and_time), HOUR(date_and_time)
            ORDER BY day_number, hour
            """
        )
        return {"data": cursor.fetchall()}
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        close_db(db, cursor)


@app.get("/dashboard/revenue")
def get_revenue_overview():
    """
    The supplied database schema has no billing date column, so a true
    time-based revenue trend cannot be calculated honestly.

    This endpoint therefore returns revenue grouped by claim status,
    which is the closest revenue visualization supported by the current schema.
    """
    db = cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                claim_status,
                COALESCE(ROUND(SUM(total_amount), 2), 0) AS revenue
            FROM billing
            GROUP BY claim_status
            ORDER BY claim_status
            """
        )
        rows = cursor.fetchall()

        for row in rows:
            row["revenue"] = float(row["revenue"] or 0)

        return {"data": rows}
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        close_db(db, cursor)


@app.get("/health")
def health():
    """Simple API health check."""
    db = cursor = None
    try:
        db = get_db()
        return {"status": "ok", "database": "connected"}
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        close_db(db, cursor)
