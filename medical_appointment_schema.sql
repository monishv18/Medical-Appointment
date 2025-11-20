-- medical_appointment_schema.sql

-- SQL schema for Medical Appointment Scheduling Agent
-- Compatible with PostgreSQL
-- Enable pgcrypto for UUID generation if available (Postgres specific).

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Table: appointment_types

CREATE TABLE IF NOT EXISTS appointment_types (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
  description TEXT
);

-- Seed appointment types

INSERT INTO appointment_types (name, duration_minutes, description)
VALUES
  ('consultation', 30, 'General consultation - 30 minutes'),
  ('followup', 15, 'Follow-up visit - 15 minutes'),
  ('physical', 45, 'Physical exam - 45 minutes'),
  ('specialist', 60, 'Specialist consultation - 60 minutes')
ON CONFLICT (name) DO NOTHING;

-- Table: doctor_schedule (weekly working hours)

CREATE TABLE IF NOT EXISTS doctor_schedule (
  id SERIAL PRIMARY KEY,
  weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6), -- 0=Sunday .. 6=Saturday
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  notes TEXT
);

-- Sample Mon-Fri 09:00-17:00

INSERT INTO doctor_schedule (weekday, start_time, end_time, notes)
VALUES
  (1, '09:00', '17:00', 'Regular hours'),
  (2, '09:00', '17:00', 'Regular hours'),
  (3, '09:00', '17:00', 'Regular hours'),
  (4, '09:00', '17:00', 'Regular hours'),
  (5, '09:00', '17:00', 'Regular hours')
ON CONFLICT DO NOTHING;

-- Table: event_types (mirrors appointment_types, optional Calendly mapping)

CREATE TABLE IF NOT EXISTS event_types (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  uuid UUID DEFAULT gen_random_uuid(),
  duration_minutes INTEGER NOT NULL
);

INSERT INTO event_types (name, duration_minutes)
SELECT name, duration_minutes FROM appointment_types
ON CONFLICT (name) DO NOTHING;

-- Table: scheduled_appointments

CREATE TABLE IF NOT EXISTS scheduled_appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  appointment_type_id INTEGER NOT NULL REFERENCES appointment_types(id) ON DELETE RESTRICT,
  patient_name TEXT NOT NULL,
  patient_email TEXT NOT NULL,
  patient_phone TEXT,
  reason TEXT,
  date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  confirmation_code TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'confirmed', -- confirmed / cancelled
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sched_date_start ON scheduled_appointments (date, start_time);
CREATE INDEX IF NOT EXISTS idx_sched_type_date ON scheduled_appointments (appointment_type_id, date);

-- Trigger function to update updated_at

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_timestamp
BEFORE UPDATE ON scheduled_appointments
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();

-- Table: clinic_faq (for RAG ingestion)

CREATE TABLE IF NOT EXISTS clinic_faq (
  id SERIAL PRIMARY KEY,
  category TEXT,
  question TEXT NOT NULL,
  answer TEXT NOT NULL
);

INSERT INTO clinic_faq (category, question, answer)
VALUES
  ('clinic_details','Where is the clinic located?','HealthCare Plus Clinic, 123 Wellness Street, Cityville. Parking available on site.'),
  ('insurance','Which insurance do you accept?','We accept Blue Cross Blue Shield, Aetna, Cigna, UnitedHealthcare, and Medicare.'),
  ('policies','What is your cancellation policy?','Please cancel at least 24 hours before your appointment to avoid charges.')
ON CONFLICT DO NOTHING;

-- Table: user_sessions (conversation state)

CREATE TABLE IF NOT EXISTS user_sessions (
  session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT,
  last_state TEXT,
  temporary_data JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_userid ON user_sessions (user_id);

CREATE TRIGGER trg_update_user_session
BEFORE UPDATE ON user_sessions
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();

-- Table: waitlist (optional)

CREATE TABLE IF NOT EXISTS waitlist (
  id SERIAL PRIMARY KEY,
  patient_name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  date DATE,
  preferred_time TIME,
  notes TEXT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Optional persisted available_slots table

CREATE TABLE IF NOT EXISTS available_slots (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  appointment_type_id INTEGER REFERENCES appointment_types(id),
  is_available BOOLEAN DEFAULT TRUE
);

-- Helper: generate_confirmation_code (short hex string)

CREATE OR REPLACE FUNCTION generate_confirmation_code()
RETURNS TEXT LANGUAGE sql AS $$
  SELECT substr(encode(digest(gen_random_uuid()::text || clock_timestamp()::text, 'sha1'), 'hex'),1,8);
$$;

-- Helper: get_working_hours_for_date(date)

CREATE OR REPLACE FUNCTION get_working_hours_for_date(p_date DATE)
RETURNS TABLE(start_time TIME, end_time TIME) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT ds.start_time, ds.end_time
  FROM doctor_schedule ds
  WHERE ds.weekday = EXTRACT(DOW FROM p_date)::INT
  ORDER BY ds.id
  LIMIT 1;
END;
$$;

-- Helper: generate_available_slots(date, appointment_type)

CREATE OR REPLACE FUNCTION generate_available_slots(p_date DATE, p_appointment_type TEXT)
RETURNS TABLE(start_time TIME, end_time TIME, is_available BOOLEAN) LANGUAGE plpgsql AS $$
DECLARE
  dur_minutes INTEGER;
  clinic_start TIME;
  clinic_end TIME;
  slot_start TIMESTAMP;
  slot_end TIMESTAMP;
BEGIN
  SELECT duration_minutes INTO dur_minutes FROM appointment_types WHERE name = p_appointment_type;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Unknown appointment_type: %', p_appointment_type;
  END IF;

  SELECT start_time, end_time INTO clinic_start, clinic_end FROM get_working_hours_for_date(p_date) LIMIT 1;
  IF clinic_start IS NULL THEN
    RETURN;
  END IF;

  slot_start := (p_date + clinic_start)::timestamp;
  slot_end := (p_date + clinic_end)::timestamp;

  WHILE slot_start + (dur_minutes || ' minutes')::interval <= slot_end LOOP
    IF EXISTS (
      SELECT 1 FROM scheduled_appointments sa
      WHERE sa.date = p_date
        AND NOT (sa.end_time <= slot_start::time OR sa.start_time >= (slot_start + (dur_minutes || ' minutes')::interval)::time)
        AND sa.status = 'confirmed'
    ) THEN
      is_available := FALSE;
    ELSE
      is_available := TRUE;
    END IF;

    start_time := slot_start::time;
    end_time := (slot_start + (dur_minutes || ' minutes')::interval)::time;
    RETURN NEXT;
    slot_start := slot_start + (dur_minutes || ' minutes')::interval;
  END LOOP;
END;
$$;

-- Helper: book_appointment(...) - atomic booking with overlap checks

CREATE OR REPLACE FUNCTION book_appointment(
  p_appointment_type TEXT,
  p_date DATE,
  p_start_time TIME,
  p_patient_name TEXT,
  p_patient_email TEXT,
  p_patient_phone TEXT,
  p_reason TEXT
)
RETURNS TABLE(booking_id UUID, status TEXT, confirmation_code TEXT) LANGUAGE plpgsql AS $$
DECLARE
  type_id INTEGER;
  dur INTEGER;
  p_end_time TIME;
  overlap_count INTEGER;
  new_id UUID;
  conf_code TEXT;
BEGIN
  SELECT id, duration_minutes INTO type_id, dur FROM appointment_types WHERE name = p_appointment_type;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Invalid appointment type: %', p_appointment_type;
  END IF;

  p_end_time := (p_start_time::timestamp + (dur || ' minutes')::interval)::time;

  IF NOT EXISTS (
    SELECT 1 FROM doctor_schedule ds
    WHERE ds.weekday = EXTRACT(DOW FROM p_date)::INT
      AND ds.start_time <= p_start_time
      AND ds.end_time >= p_end_time
  ) THEN
    RAISE EXCEPTION 'Requested time is outside working hours.';
  END IF;

  SELECT COUNT(*) INTO overlap_count FROM scheduled_appointments sa
  WHERE sa.date = p_date
    AND NOT (sa.end_time <= p_start_time OR sa.start_time >= p_end_time)
    AND sa.status = 'confirmed';

  IF overlap_count > 0 THEN
    RAISE EXCEPTION 'Time slot not available.';
  END IF;

  conf_code := generate_confirmation_code();

  INSERT INTO scheduled_appointments (
    appointment_type_id, patient_name, patient_email, patient_phone, reason,
    date, start_time, end_time, confirmation_code, status
  ) VALUES (
    type_id, p_patient_name, p_patient_email, p_patient_phone, p_reason,
    p_date, p_start_time, p_end_time, conf_code, 'confirmed'
  ) RETURNING id INTO new_id;

  booking_id := new_id;
  status := 'confirmed';
  confirmation_code := conf_code;
  RETURN NEXT;
END;
$$;

-- End of SQL schema

