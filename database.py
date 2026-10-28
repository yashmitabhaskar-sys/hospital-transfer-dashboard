
import sqlite3
from datetime import datetime

DB_NAME = "referralloop.db"


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def connect():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_table():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                sending TEXT NOT NULL,
                receiving TEXT NOT NULL,
                reason TEXT NOT NULL,
                summary TEXT,
                status TEXT NOT NULL DEFAULT 'Sent'
            )
        """)

        # Upgrade existing referral databases safely.
        referral_columns = {
            row[1] for row in
            conn.execute("PRAGMA table_info(referrals)").fetchall()
        }

        if "documents_provided" not in referral_columns:
            conn.execute("""
                ALTER TABLE referrals
                ADD COLUMN documents_provided TEXT DEFAULT ''
            """)

        if "documents_required" not in referral_columns:
            conn.execute("""
                ALTER TABLE referrals
                ADD COLUMN documents_required TEXT DEFAULT ''
            """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS handover_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referral_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                event_time TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY (referral_id)
                    REFERENCES referrals(id) ON DELETE CASCADE
            )
        """)

        # Upgrade the event table if it was created by an older version.
        event_columns = {
            row[1] for row in
            conn.execute("PRAGMA table_info(handover_events)").fetchall()
        }

        if "details" not in event_columns:
            conn.execute("""
                ALTER TABLE handover_events
                ADD COLUMN details TEXT
            """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS medical_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                entry TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS patient_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                file_name TEXT NOT NULL,
                content_type TEXT,
                file_data BLOB NOT NULL,
                uploaded_at TEXT NOT NULL,
                review_status TEXT NOT NULL DEFAULT 'Pending'
            )
        """)

        # Give existing referrals an initial history event if needed.
        conn.execute("""
            INSERT INTO handover_events
                (referral_id, status, event_time, details)
            SELECT r.id, r.status, ?, 'Existing referral'
            FROM referrals r
            WHERE NOT EXISTS (
                SELECT 1 FROM handover_events e
                WHERE e.referral_id = r.id
            )
        """, (now(),))


# -----------------------------
# REFERRALS
# -----------------------------

def add_referral(
    patient_id,
    sending,
    receiving,
    reason,
    summary,
    documents_provided="",
    documents_required="",
):
    with connect() as conn:
        cursor = conn.execute("""
            INSERT INTO referrals (
                patient_id, sending, receiving, reason, summary,
                status, documents_provided, documents_required
            )
            VALUES (?, ?, ?, ?, ?, 'Sent', ?, ?)
        """, (
            patient_id,
            sending,
            receiving,
            reason,
            summary,
            documents_provided,
            documents_required,
        ))

        referral_id = cursor.lastrowid

        conn.execute("""
            INSERT INTO handover_events
                (referral_id, status, event_time, details)
            VALUES (?, 'Sent', ?, 'Referral created')
        """, (referral_id, now()))

        return referral_id


def get_referrals():
    with connect() as conn:
        return conn.execute("""
            SELECT id, patient_id, sending, receiving,
                   reason, summary, status,
                   documents_provided, documents_required
            FROM referrals
            ORDER BY id DESC
        """).fetchall()


def update_status(referral_id, new_status, details=""):
    transitions = {
        "Sent": ["Received", "Rejected"],
        "Received": ["Accepted", "Rejected"],
        "Accepted": ["Completed"],
    }

    with connect() as conn:
        row = conn.execute(
            "SELECT status FROM referrals WHERE id = ?",
            (referral_id,),
        ).fetchone()

        if row is None:
            return False

        if new_status not in transitions.get(row[0], []):
            return False

        conn.execute("""
            UPDATE referrals
            SET status = ?
            WHERE id = ?
        """, (new_status, referral_id))

        conn.execute("""
            INSERT INTO handover_events
                (referral_id, status, event_time, details)
            VALUES (?, ?, ?, ?)
        """, (referral_id, new_status, now(), details or None))

        return True


def delete_referral(referral_id):
    with connect() as conn:
        conn.execute(
            "DELETE FROM handover_events WHERE referral_id = ?",
            (referral_id,),
        )
        cursor = conn.execute(
            "DELETE FROM referrals WHERE id = ?",
            (referral_id,),
        )
        return cursor.rowcount > 0


def get_events(referral_id):
    with connect() as conn:
        return conn.execute("""
            SELECT status, event_time, details
            FROM handover_events
            WHERE referral_id = ?
            ORDER BY id ASC
        """, (referral_id,)).fetchall()


# -----------------------------
# PATIENT DOCUMENT UPLOADS
# -----------------------------

def add_patient_upload(
    patient_id,
    file_name,
    content_type,
    file_data,
):
    with connect() as conn:
        conn.execute("""
            INSERT INTO patient_uploads (
                patient_id, file_name, content_type,
                file_data, uploaded_at, review_status
            )
            VALUES (?, ?, ?, ?, ?, 'Pending')
        """, (
            patient_id,
            file_name,
            content_type,
            sqlite3.Binary(file_data),
            now(),
        ))


def get_patient_uploads(patient_id):
    with connect() as conn:
        return conn.execute("""
            SELECT id, patient_id, file_name, content_type,
                   uploaded_at, review_status
            FROM patient_uploads
            WHERE patient_id = ?
            ORDER BY id DESC
        """, (patient_id,)).fetchall()


def get_all_patient_uploads():
    with connect() as conn:
        return conn.execute("""
            SELECT id, patient_id, file_name, content_type,
                   uploaded_at, review_status
            FROM patient_uploads
            ORDER BY id DESC
        """).fetchall()


def get_upload_file(upload_id):
    with connect() as conn:
        return conn.execute("""
            SELECT file_name, content_type, file_data
            FROM patient_uploads
            WHERE id = ?
        """, (upload_id,)).fetchone()


def mark_upload_reviewed(upload_id):
    with connect() as conn:
        cursor = conn.execute("""
            UPDATE patient_uploads
            SET review_status = 'Reviewed'
            WHERE id = ?
        """, (upload_id,))
        return cursor.rowcount > 0


# -----------------------------
# OFFICIAL MEDICAL HISTORY
# -----------------------------

def add_medical_history(patient_id, entry, doctor_name):
    with connect() as conn:
        conn.execute("""
            INSERT INTO medical_history (
                patient_id, entry, doctor_name, created_at
            )
            VALUES (?, ?, ?, ?)
        """, (patient_id, entry, doctor_name, now()))


def get_medical_history(patient_id):
    with connect() as conn:
        return conn.execute("""
            SELECT id, patient_id, entry, doctor_name, created_at
            FROM medical_history
            WHERE patient_id = ?
            ORDER BY id DESC
        """, (patient_id,)).fetchall()


def delete_medical_history(history_id):
    with connect() as conn:
        cursor = conn.execute(
            "DELETE FROM medical_history WHERE id = ?",
            (history_id,),
        )
        return cursor.rowcount > 0
