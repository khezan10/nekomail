import sqlite3
import asyncio
import logging
from database import DB_FILE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_old_emails():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Hapus data yang umurnya lebih dari 1 hari
        query = "DELETE FROM emails WHERE created_at <= datetime('now', '-1 day');"
        cursor.execute(query)
        deleted_count = cursor.rowcount
        conn.commit()
        
        if deleted_count > 0:
            logger.info(f"Pembersihan berhasil: {deleted_count} email lama dihapus.")
    except Exception as e:
        logger.error(f"Error saat pembersihan: {e}")
    finally:
        conn.close()

async def start_daily_cleanup():
    logger.info("Tugas pembersihan otomatis (1 hari sekali) mulai berjalan...")
    while True:
        delete_old_emails()
        await asyncio.sleep(86400) # Tidur selama 24 jam