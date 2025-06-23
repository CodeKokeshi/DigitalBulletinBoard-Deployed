from fastapi import FastAPI, Request, Depends, HTTPException, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer

import hashlib
import uvicorn
import logging
import os
import json
import smtplib
import random
import asyncio
from encrypted_db import EncryptedDatabase
from secure_config import secure_config
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from runtime_scheduler import check_runtime_allowed, scheduler

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

# Production configuration
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Load secure configuration (now encrypted!)
email_config = secure_config.get_email_config()
secret_keys = secure_config.get_secret_keys()

# Email configuration (now from encrypted source)
EMAIL_ADDRESS = email_config["email_sender"]
EMAIL_PASSWORD = email_config["password"]

# This is a dictionary that will store the verification codes for each email.
VERIFICATION_CODES = {}

# This has little to no use now because we're now using bootstrap for the frontend.
# But it's still here because I don't know whether some files are still using it.
version = f"{int(datetime.now().timestamp())}" + f"{random.randint(1, 1000)}"

# Sends verification codes to email address depending whether for resetting password or signing up.
async def send_verification_email(to_email, code):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = "Your Verification Code"
        body = f"Your verification code is {code}."
        msg.attach(MIMEText(body, 'plain'))

        # Run the SMTP operations in a separate thread
        await asyncio.to_thread(send_email_sync, msg)

        print("Verification email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Another part of email sending.
def send_email_sync(msg):
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# I'm not sure whether I'm still using this one.
def verification_confirmed(to_email):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = "Email Verified"
        body = f"""
        Your email has been verified.
        """
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail and send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Verification email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

SECRET_KEY = secret_keys["user_key"]
serializer = URLSafeTimedSerializer(SECRET_KEY)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware for managing sessions
# CORS and Trusted Host middleware for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else ALLOWED_HOSTS,  # Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  # Only allow needed methods
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS
)

# CORS and Trusted Host middleware for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production to specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Runtime scheduler middleware - check if app should be running
@app.middleware("http")
async def runtime_check_middleware(request, call_next):
    # Allow health checks and static files during downtime
    if request.url.path in ["/health", "/favicon.ico"] or request.url.path.startswith("/static"):
        return await call_next(request)
    
    # Check if runtime is allowed
    try:
        check_runtime_allowed()
    except HTTPException as e:
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=e.detail, status_code=e.status_code)
    
    return await call_next(request)

# Database and other setup...
encrypted_db = EncryptedDatabase()

logging.basicConfig(level=logging.DEBUG)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

class User(BaseModel):
    fullName: str
    age: int
    email: str
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Load data.json
DATA_FILE = os.path.join("static", "data", "data.json")

def load_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

# Save data to JSON
def save_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

announcement_data = load_data(DATA_FILE)

def get_current_user(session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=303, detail="Redirect", headers={"Location": "/homepage"})
    try:
        email = serializer.loads(session_token)
        return email
    except Exception:
        raise HTTPException(status_code=303, detail="Redirect", headers={"Location": "/homepage"})


@app.get("/health")
async def health_check():
    """Health check endpoint - always available"""
    schedule_info = scheduler.get_schedule_info()
    return {
        "status": "healthy",
        "runtime_allowed": schedule_info["is_running"],
        "schedule": schedule_info
    }

@app.get("/schedule")
async def get_schedule():
    """Get current schedule information"""
    return scheduler.get_schedule_info()

# Main routes start here
@app.get("/announcement/{announcement_id}", response_class=HTMLResponse)
async def display_announcement(announcement_id: int, request: Request, session_token: str = Cookie(None)):
    # Reload the announcement data
    announcement_data = load_data(DATA_FILE)
    user = None

    if session_token:
        try:
            user = serializer.loads(session_token)
        except Exception:
            pass

    for section in announcement_data.values():
        for announcement in section:
            if announcement["announcement_id"] == announcement_id:
                comments = announcement.get("comments", [])
                likes = announcement["likes"]["amount"]
                return templates.TemplateResponse(
                    "announcement.html",
                    {
                        "version": version,
                        "request": request,
                        "title": announcement["title"],
                        "date": announcement["date"],
                        "description": announcement.get("description", "No description available."),
                        "user": user,
                        "comments": comments,
                        "likes": likes,
                        "announcement_id": announcement_id,
                        "image_attachment": announcement.get("image_attachment")
                    }
                )
    raise HTTPException(status_code=404, detail="Announcement not found")

@app.get("/feedback", response_class=HTMLResponse)
async def read_feedback(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("feedback.html", {"request": request, "user": user, "version": version})

@app.get("/unauthorized", response_class=HTMLResponse)
async def unauthorized_page(request: Request):
    return templates.TemplateResponse("unauthorized.html", {"request": request})

@app.post("/submit_feedback")
async def submit_feedback(request: Request, user: str = Depends(get_current_user)):
    form = await request.form()
    title = form.get('title')
    description = form.get('description')
    attachment = form.get('attachment')

    if not title or not description:
        return JSONResponse({"message": "Title and description are required."}, status_code=400)

    feedback_data = load_data("static/data/feedback.json")
    feedback_id = max([fb["feedback_id"] for fb in feedback_data["feedbacks"]], default=0) + 1

    feedback = {
        "email": user,
        "feedback_title": title,
        "feedback_description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feedback_id": feedback_id
    }

    if attachment:
        directory = "static/images/Feedback/"
        file_extension = os.path.splitext(attachment.filename)[1]
        new_filename = f"{feedback_id}{file_extension}"
        attachment_path = os.path.join(directory, new_filename)
        with open(attachment_path, "wb") as f:
            f.write(await attachment.read())
        feedback["image_attachment"] = f"/{attachment_path}"

    feedback_data["feedbacks"].append(feedback)

    # Update the current value
    feedback_data["update"][0]["before"] = feedback_data["update"][0]["current"]
    feedback_data["update"][0]["current"] += 1

    save_data("static/data/feedback.json", feedback_data)

    return JSONResponse({"message": "Feedback submitted successfully."}, status_code=200)

from better_profanity import profanity

@app.post("/announcement/{announcement_id}/comment")
async def add_comment(announcement_id: int, comment: str = Form(...), user: str = Depends(get_current_user)):
    # Check for profanity in the comment
    if profanity.contains_profanity(comment):
        raise HTTPException(status_code=400, detail="The comment contains obscene language.")

    user_data = encrypted_db.get_user_by_email(user)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    username = user_data["full_name"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_comment = {
        "username": username,
        "comment": comment,
        "date": date,
        "email": user
    }

    announcement_data = load_data(DATA_FILE)
    for section in announcement_data.values():
        for announcement in section:
            if announcement["announcement_id"] == announcement_id:
                if "comments" not in announcement:
                    announcement["comments"] = []
                announcement["comments"].append(new_comment)
                save_data(DATA_FILE, announcement_data)
                return JSONResponse({"username": username, "comment": comment, "date": date})

    raise HTTPException(status_code=404, detail="Announcement not found")


@app.delete("/announcement/{announcement_id}/comment/{comment_index}")
async def delete_comment(announcement_id: int, comment_index: int, user: str = Depends(get_current_user)):
    announcement_data = load_data(DATA_FILE)
    for section in announcement_data.values():
        for announcement in section:
            if announcement["announcement_id"] == announcement_id:
                if "comments" in announcement and len(announcement["comments"]) > comment_index:
                    comment = announcement["comments"][comment_index]
                    if comment["email"] != user:
                        raise HTTPException(status_code=403, detail="You can only delete your own comments")
                    del announcement["comments"][comment_index]
                    save_data(DATA_FILE, announcement_data)
                    return JSONResponse({"message": "Comment deleted successfully"})
    raise HTTPException(status_code=404, detail="Announcement or comment not found")

@app.post("/announcement/{announcement_id}/like")
async def like_announcement(announcement_id: int, user: str = Depends(get_current_user)):
    announcement_data = load_data(DATA_FILE)
    for section in announcement_data.values():
        for announcement in section:
            if announcement["announcement_id"] == announcement_id:
                if user in announcement["likes"]["accounts"]:
                    announcement["likes"]["accounts"].remove(user)
                    announcement["likes"]["amount"] -= 1
                else:
                    announcement["likes"]["accounts"].append(user)
                    announcement["likes"]["amount"] += 1
                save_data(DATA_FILE, announcement_data)
                return JSONResponse({"likes": announcement["likes"]["amount"]})
    raise HTTPException(status_code=404, detail="Announcement not found")

@app.get("/signup_verification", response_class=HTMLResponse)
async def signup_verification_page(request: Request):
    return templates.TemplateResponse("signup_verification.html", {"request": request})

@app.post("/verify_code")
async def verify_code(data: dict):
    email = data.get('email')
    code = data.get('code')

    if not email or not code:
        return JSONResponse({"message": "Email and code are required."}, status_code=400)

    if email in VERIFICATION_CODES and VERIFICATION_CODES[email]["code"] == code:
        user_data = VERIFICATION_CODES[email]["user_data"]

        # Write user data to the encrypted database
        hashed_password = hash_password(user_data["password"])
        success = encrypted_db.create_user(
            full_name=user_data["fullName"],
            age=user_data["age"],
            email=user_data["email"],
            password=hashed_password
        )
        
        if success:
            del VERIFICATION_CODES[email]
            return RedirectResponse(url="/", status_code=303)  # Redirect to login
        else:
            return JSONResponse({"message": "Failed to create user account"}, status_code=500)
    else:
        return JSONResponse({"message": "Invalid verification code"}, status_code=400)

@app.post("/resend-code")
async def resend_code(data: dict):
    email = data.get('email')
    if not email:
        return JSONResponse({"message": "Email is required."}, status_code=400)

    if email in VERIFICATION_CODES:
        verification_code = VERIFICATION_CODES[email]["code"]
        asyncio.create_task(send_verification_email(email, verification_code))  # type: ignore
        return JSONResponse({"message": "Verification code resent."}, status_code=200)
    else:
        return JSONResponse({"message": "Email not found."}, status_code=404)

@app.post("/signup")
@limiter.limit("3/minute")  # Limit signup attempts
async def read_signup(request: Request, user: User):
    # Check if email already exists
    existing_user = encrypted_db.get_user_by_email(user.email)
    if existing_user:
        return JSONResponse({"message": "Email already exists"}, status_code=400)

    # Generate and store verification code
    verification_code = f"{random.randint(100000, 999999)}"
    VERIFICATION_CODES[user.email] = {
        "code": verification_code,
        "user_data": user.model_dump()  # Store user data temporarily
    }

    # Send email asynchronously
    asyncio.create_task(send_verification_email(user.email, verification_code))

    # Redirect to the verification page immediately
    return RedirectResponse(url=f"/signup_verification?email={user.email}", status_code=303)

@app.post("/login")
@limiter.limit("5/minute")  # Limit login attempts
async def read_login(request: Request):
    credentials = await request.json()
    email = credentials['email']
    password = hash_password(credentials['password'])

    # Retrieve user data from the encrypted database
    user = encrypted_db.get_user_by_email(email)

    if user and user["password"] == password:
        # Create a session token
        session_token = serializer.dumps(email)  # Tokenized email for session
        response = RedirectResponse(url="/homepage", status_code=303)
        response.set_cookie(key="session_token", value=session_token, httponly=True, secure=not DEBUG)
        return response

    return JSONResponse({"message": "Login failed"}, status_code=401)

@app.get("/login_form", response_class=HTMLResponse)
async def read_login_form(request: Request, session_token: str = Cookie(None)):
    if session_token:
        # Redirect logged-in users to homepage
        return RedirectResponse(url="/homepage", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "version": version})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, session_token: str = Cookie(None)):
    if session_token:
        # Redirect logged-in users to homepage
        return RedirectResponse(url="/homepage", status_code=303)
    return templates.TemplateResponse("guest_view.html", {"request": request, "version": version})

@app.get("/signup_form", response_class=HTMLResponse)
async def read_signup_form(request: Request, session_token: str = Cookie(None)):
    if session_token:
        # Redirect logged-in users to homepage
        return RedirectResponse(url="/homepage", status_code=303)
    return templates.TemplateResponse("signup.html", {"request": request, "version": version})

# opens up in new tab when terms and conditions is clicked
@app.get("/terms", response_class=HTMLResponse)
async def read_terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})

@app.get("/homepage", response_class=HTMLResponse)
async def read_homepage(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("homepage.html", {"request": request, "user": user, "version": version})

@app.get("/upcoming", response_class=HTMLResponse)
async def read_upcoming(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("upcoming.html", {"request": request, "user": user, "version": version})

@app.get("/important", response_class=HTMLResponse)
async def read_important(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("important.html", {"request": request, "user": user, "version": version})

@app.get("/upcoming_guest", response_class=HTMLResponse)
async def read_upcoming_guest(request: Request):
    return templates.TemplateResponse("upcoming_guest.html", {"request": request, "version": version})

@app.get("/important_guest", response_class=HTMLResponse)
async def read_important_guest(request: Request):
    return templates.TemplateResponse("important_guest.html", {"request": request, "version": version})

@app.get("/milestones", response_class=HTMLResponse)
async def read_milestones(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("milestones.html", {"request": request, "user": user, "version": version})

@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="session_token")
    return response

@app.get("/forgot_password", response_class=HTMLResponse)
async def forgot_password_page(request: Request, session_token: str = Cookie(None)):
    if session_token:
        # Redirect logged-in users to homepage
        return RedirectResponse(url="/homepage", status_code=303)
    return templates.TemplateResponse("forgot_password.html", {"request": request, "version": version})

@app.post("/forgot_password/send_verification_code")
@limiter.limit("3/minute")  # Limit password reset attempts
async def forgot_password_send_verification_code(request: Request, email: str = Form(...)):
    user = encrypted_db.get_user_by_email(email)
    if not user:
        return JSONResponse({"message": "Email not found"}, status_code=404)

    verification_code = f"{random.randint(100000, 999999)}"
    VERIFICATION_CODES[email] = verification_code
    await send_verification_email(email, verification_code)
    return JSONResponse({"message": "Verification code sent"}, status_code=200)

@app.post("/forgot_password/verify_code")
async def forgot_password_verify_code(email: str = Form(...), code: str = Form(...)):
    if email in VERIFICATION_CODES and VERIFICATION_CODES[email] == code:
        return JSONResponse({"message": "Code verified"}, status_code=200)
    return JSONResponse({"message": "Invalid verification code"}, status_code=400)

@app.post("/forgot_password/reset_password")
async def forgot_password_reset_password(email: str = Form(...), new_password: str = Form(...)):
    hashed_password = hash_password(new_password)
    success = encrypted_db.update_user_password(email, hashed_password)
    if success:
        # Clean up verification code
        if email in VERIFICATION_CODES:
            del VERIFICATION_CODES[email]
        return RedirectResponse(url="/", status_code=303)
    else:
        return JSONResponse({"message": "Failed to update password"}, status_code=500)

@app.get("/archives", response_class=HTMLResponse)
async def read_archives(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("archived.html", {"request": request, "user": user, "version": version})

@app.get("/archives/{archive_id}", response_class=HTMLResponse)
async def read_archives_section(archive_id: int, request: Request, user: str = Depends(get_current_user)):
    archived_data = load_data("static/data/archived_data.json")

    for section in archived_data.values():
        for announcement in section:
            if announcement["archive_id"] == archive_id:
                comments = announcement.get("comments", [])
                return templates.TemplateResponse(
                    "archived_announcement.html",
                    {
                        "request": request,
                        "title": announcement["title"],
                        "date": announcement["date"],
                        "description": announcement.get("description", "No description available."),
                        "likes": announcement["likes"]["amount"],
                        "announcement_id": announcement["announcement_id"],
                        "image_attachment": announcement.get("image_attachment"),
                        "comments": comments
                    }
                )
    raise HTTPException(status_code=404, detail="Announcement not found")

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("four-o-four.html", {"request": request}, status_code=404)
    elif exc.status_code == 303:
        return templates.TemplateResponse("unauthorized.html", {"request": request}, status_code=303)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse({"detail": exc.errors()}, status_code=400)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )