-- ============================================================
-- CARESYNC DATABASE
-- ============================================================

CREATE DATABASE IF NOT EXISTS caresync
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE caresync;


-- ============================================================
-- DROP OLD TABLES
-- ============================================================

DROP TABLE IF EXISTS activity_log;
DROP TABLE IF EXISTS billing;
DROP TABLE IF EXISTS medical_record;
DROP TABLE IF EXISTS appointment;
DROP TABLE IF EXISTS billing_staff;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS doctor;
DROP TABLE IF EXISTS patient;


-- ============================================================
-- 1. PATIENT
-- ============================================================

CREATE TABLE patient (
    patient_id       INT NOT NULL AUTO_INCREMENT,
    name             VARCHAR(150) NOT NULL,
    email            VARCHAR(150) NOT NULL,
    password_hash    VARCHAR(255) NOT NULL,
    date_of_birth    DATE NOT NULL,
    contact          VARCHAR(15),
    address          TEXT,
    blood_group      VARCHAR(5),
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                     ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (patient_id),

    UNIQUE KEY uq_patient_email (email),

    INDEX idx_patient_name (name)
);


-- ============================================================
-- 2. DOCTOR
-- ============================================================

CREATE TABLE doctor (
    doctor_id        INT NOT NULL AUTO_INCREMENT,
    name             VARCHAR(150) NOT NULL,
    specialization   VARCHAR(100) NOT NULL,
    contact          VARCHAR(15),
    email            VARCHAR(150) NOT NULL,
    password_hash    VARCHAR(255) NOT NULL,
    is_active        TINYINT(1) NOT NULL DEFAULT 1,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (doctor_id),

    UNIQUE KEY uq_doctor_email (email)
);


-- ============================================================
-- 3. ADMIN
-- ============================================================

CREATE TABLE admin (
    admin_id         INT NOT NULL AUTO_INCREMENT,
    name             VARCHAR(150) NOT NULL,
    email            VARCHAR(150) NOT NULL,
    password_hash    VARCHAR(255) NOT NULL,
    contact          VARCHAR(15),
    role             VARCHAR(50) NOT NULL,

    PRIMARY KEY (admin_id),

    UNIQUE KEY uq_admin_email (email)
);


-- ============================================================
-- 4. BILLING STAFF
-- ============================================================

CREATE TABLE billing_staff (
    billing_staff_id   INT NOT NULL AUTO_INCREMENT,
    name               VARCHAR(150) NOT NULL,
    contact            VARCHAR(15),
    email              VARCHAR(150) NOT NULL,
    password_hash      VARCHAR(255) NOT NULL,
    is_active          TINYINT(1) NOT NULL DEFAULT 1,
    department         VARCHAR(100),

    PRIMARY KEY (billing_staff_id),

    UNIQUE KEY uq_billing_staff_email (email)
);


-- ============================================================
-- 5. APPOINTMENT
-- ============================================================

CREATE TABLE appointment (
    appointment_id     INT NOT NULL AUTO_INCREMENT,
    patient_id         INT NOT NULL,
    doctor_id          INT NOT NULL,
    date_and_time      DATETIME NOT NULL,
    reason             TEXT,
    status             ENUM('Scheduled', 'Completed', 'Cancelled')
                       NOT NULL DEFAULT 'Scheduled',

    PRIMARY KEY (appointment_id),

    CONSTRAINT fk_appointment_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_appointment_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctor(doctor_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_appointment_patient (patient_id),
    INDEX idx_appointment_doctor (doctor_id),
    INDEX idx_appointment_datetime (date_and_time)
);


-- ============================================================
-- 6. MEDICAL RECORD
-- ============================================================

CREATE TABLE medical_record (
    medical_record_id   INT NOT NULL AUTO_INCREMENT,
    patient_id          INT NOT NULL,
    doctor_id           INT NOT NULL,
    medical_history     TEXT,
    diagnosis           TEXT,
    prescription        TEXT,
    test_name           VARCHAR(150),
    test_result         TEXT,

    PRIMARY KEY (medical_record_id),

    CONSTRAINT fk_medical_record_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_medical_record_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctor(doctor_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_medical_record_patient (patient_id),
    INDEX idx_medical_record_doctor (doctor_id)
);


-- ============================================================
-- 7. BILLING
-- ============================================================

CREATE TABLE billing (
    bill_id             INT NOT NULL AUTO_INCREMENT,
    patient_id          INT NOT NULL,
    total_amount        DECIMAL(10,2) NOT NULL,
    insurance_provider  VARCHAR(150),
    claim_amount        DECIMAL(10,2),
    claim_status        ENUM('Pending', 'Approved', 'Rejected')
                        NOT NULL DEFAULT 'Pending',
    rejection_reason    TEXT,

    PRIMARY KEY (bill_id),

    CONSTRAINT fk_billing_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_billing_patient (patient_id),
    INDEX idx_billing_claim_status (claim_status),

    CONSTRAINT chk_billing_total
        CHECK (total_amount >= 0),

    CONSTRAINT chk_billing_claim
        CHECK (claim_amount IS NULL OR claim_amount >= 0)
);


-- ============================================================
-- 8. ACTIVITY LOG
-- ============================================================

CREATE TABLE activity_log (
    log_id          BIGINT NOT NULL AUTO_INCREMENT,
    user_type       ENUM('Patient', 'Doctor', 'Admin', 'Billing Staff')
                    NOT NULL,
    user_id         INT NOT NULL,
    action          VARCHAR(100) NOT NULL,
    target_table    VARCHAR(50),
    target_id       INT,
    logged_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (log_id),

    INDEX idx_activity_user (user_type, user_id),
    INDEX idx_activity_action (action),
    INDEX idx_activity_time (logged_at)
);


-- ============================================================
-- VERIFY TABLES
-- ============================================================

SHOW TABLES;