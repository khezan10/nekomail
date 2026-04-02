from fastapi import FastAPI, Request, Form, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import os
import email
from email.policy import default
import pam
import uuid


from database import init_db
import crud
from cleanup_task import start_daily_cleanup

# === SISTEM LOGIN (SESI SEDERHANA) ===
active_sessions = {}

def check_auth(request: Request):
    """Fungsi untuk mengecek apakah user sudah login"""
    token = request.cookies.get("nekomail_session")
    if not token or token not in active_sessions:
        raise HTTPException(status_code=401, detail="Akses ditolak. Silakan login.")
    return active_sessions[token]

# === LIFESPAN (Pengganti on_event startup) ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db() 
    cleanup_task = asyncio.create_task(start_daily_cleanup()) 
    yield
    cleanup_task.cancel() 

app = FastAPI(title="Nekomail Backend API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailWebhook(BaseModel):
    sender: str
    recipient: str
    subject: str
    body_text: str
    body_html: str = ""

# --- ENDPOINT AUTHENTICATION ---
@app.post("/api/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    p = pam.pam()
    # Mengecek username dan password ke sistem Linux Armbian
    if p.authenticate(username, password):
        session_token = str(uuid.uuid4())
        active_sessions[session_token] = username
        response.set_cookie(key="nekomail_session", value=session_token, httponly=True, max_age=86400)
        return {"status": "success"}
    return {"status": "error", "message": "Username atau Password Linux salah!"}

@app.post("/api/logout")
async def logout(response: Response, request: Request):
    token = request.cookies.get("nekomail_session")
    if token in active_sessions:
        del active_sessions[token]
    response.delete_cookie("nekomail_session")
    return {"status": "success"}

# --- ENDPOINT 1: Webhook untuk menerima & MEMBEDAH email ---
@app.post("/webhook/email")
async def receive_email(webhook_data: EmailWebhook):
    msg = email.message_from_string(webhook_data.body_text, policy=default)
    
    real_text = ""
    real_html = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = str(part.get_content_disposition())
            if "attachment" in content_disposition:
                continue 
            
            content_type = part.get_content_type()
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    decoded = payload.decode(charset, errors='replace')
                    
                    if content_type == "text/plain" and not real_text:
                        real_text = decoded
                    elif content_type == "text/html" and not real_html:
                        real_html = decoded
            except Exception as e:
                print(f"Gagal membedah bagian email: {e}")
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                decoded = payload.decode(charset, errors='replace')
                if msg.get_content_type() == "text/html":
                    real_html = decoded
                else:
                    real_text = decoded
        except Exception as e:
            print(f"Gagal membedah body email: {e}")


    final_text = real_text or webhook_data.body_text
    final_html = real_html or webhook_data.body_html

    email_id = crud.create_email(
        sender=webhook_data.sender,
        recipient=webhook_data.recipient,
        subject=webhook_data.subject,
        body_text=final_text, 
        body_html=final_html
    )
    return {"status": "success", "message": "Email tersimpan", "id": email_id}

# --- ENDPOINT 2: API untuk Frontend (DIPROTEKSI LOGIN) ---
@app.get("/api/inbox/{recipient_email}")
async def get_inbox(recipient_email: str, _ = Depends(check_auth)):
    emails = crud.get_emails_by_recipient(recipient_email)
    return {
        "status": "success",
        "recipient": recipient_email, 
        "total": len(emails),
        "data": emails
    }

# --- ROUTING TAMPILAN WEB ---
@app.get("/")
async def root(request: Request):
    # Cek apakah user sudah login
    token = request.cookies.get("nekomail_session")
    if token and token in active_sessions:
        if os.path.exists("frontend/inbox.html"):
            return FileResponse("frontend/inbox.html")
        return {"Error": "File frontend/inbox.html tidak ditemukan."}
    
    # Jika belum login, tampilkan halaman login
    if os.path.exists("frontend/login.html"):
        return FileResponse("frontend/login.html")
    return {"Error": "File frontend/login.html tidak ditemukan."}

# Mount folder frontend agar file JS/CSS bisa diakses via /static
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
