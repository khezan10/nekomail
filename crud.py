from database import get_db_connection

def create_email(sender: str, recipient: str, subject: str, body_text: str, body_html: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Bersihkan spasi kosong di awal/akhir dan jadikan huruf kecil semua
    clean_recipient = recipient.strip().lower() 
    
    cursor.execute("""
        INSERT INTO emails (sender, recipient, subject, body_text, body_html)
        VALUES (?, ?, ?, ?, ?)
    """, (sender, clean_recipient, subject, body_text, body_html))
    conn.commit()
    email_id = cursor.lastrowid
    conn.close()
    return email_id

def get_emails_by_recipient(recipient: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Gunakan LIKE agar mengabaikan huruf besar/kecil dan format <email>
    search_term = f"%{recipient.strip().lower()}%"
    
    cursor.execute("""
        SELECT * FROM emails 
        WHERE recipient LIKE ? 
        ORDER BY created_at DESC
    """, (search_term,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]