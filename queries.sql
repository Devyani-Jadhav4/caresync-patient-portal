-- CareSync Doctor Appointment Summary

USE caresync;

SELECT
    d.name AS doctor_name,
    COUNT(a.appointment_id) AS total_appointments
FROM doctor d
JOIN appointment a
    ON d.doctor_id = a.doctor_id
GROUP BY d.name
ORDER BY total_appointments DESC;