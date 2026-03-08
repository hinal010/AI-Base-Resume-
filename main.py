from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

from crud import create_user, get_user_by_email,get_user_profile,update_user_profile
from auth import verify_password
from jwt_token import create_access_token, verify_token
from auth_config import CLIENT_ID, CLIENT_SECRET, GOOGLE_REDIRECT_URI,SESSION_SECRET_KEY
from authlib.integrations.starlette_client import OAuth
import models  

templates = Jinja2Templates(directory="template")
app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY
)

oauth = OAuth()

oauth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    },
    redirect_uri=GOOGLE_REDIRECT_URI
)
@app.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def google_callback(request: Request):
    # Get Google token
    token = await oauth.google.authorize_access_token(request)

    # Get user info from Google
    resp = await oauth.google.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        token=token
    )
    user_info = resp.json()
    if not user_info:
        return {"error": "Google login failed"}

    email = user_info["email"]
    name = user_info.get("name", email.split("@")[0])

    # Check if user exists in DB
    user = get_user_by_email(email)
    if not user:
        # If not exist, create a new user
        create_user(
            username=name,
            full_name=name,
            email=email,
            password="google_auth"  # mark as google login
        )

    # Create JWT access token
    access_token = create_access_token({"user_id": user["id"], "email": user["email"]})
    # Redirect to index page
    response = RedirectResponse("/index", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True
    )
    return response

@app.get("/index", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login",response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@app.get("/register",response_class=HTMLResponse)
def register(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})

@app.get("/profile",response_class=HTMLResponse)
def profile(request:Request):
    return templates.TemplateResponse("profile.html",{"request":request})

@app.get("/forgot_password",response_class=HTMLResponse)
def forgotpass(request:Request):
    return templates.TemplateResponse("forgot_password.html",{"request":request})

@app.post("/register")
def register(
    username: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    create_user(username, full_name, email, password)
    return RedirectResponse("/login", status_code=302)

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):

    user = get_user_by_email(email)

    if not user:
        return {"error": "User not found"}

    if not verify_password(password, user["hashed_password"]):
        return {"error": "Incorrect password"}

    access_token = create_access_token({"user_id": user["id"], "email": user["email"]})


    response = RedirectResponse("/index", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return response

@app.get("/logout")
def logout():
    response = RedirectResponse(
        "https://accounts.google.com/Logout",  # Google logout URL
        status_code=302
    )
    # Remove your JWT cookie
    response.delete_cookie(key="access_token")
    return response

# @app.get("/profile", response_class=HTMLResponse)
# def profile_page(request: Request, current_user=Depends(get_current_user)):
#     if not current_user:
#         return RedirectResponse("/login")
#     user_profile = get_user_profile(current_user)
#     return templates.TemplateResponse("profile.html", {"request": request, "profile": user_profile})


# @app.post("/profile")
# def update_profile(
#     request: Request,
#     phone: str = Form(None),
#     location: str = Form(None),
#     profile_image: UploadFile = File(None),
#     current_user=Depends(get_current_user)
# ):
#     if not current_user:
#         return RedirectResponse("/login")

#     image_path = None
#     if profile_image:
#         import os
#         os.makedirs("static/images", exist_ok=True)
#         image_path = f"static/images/{profile_image.filename}"
#         with open(image_path, "wb") as f:
#             f.write(profile_image.file.read())

#     update_user_profile(
#         user_id=current_user,
#         phone=phone,
#         location=location,
#         profile_image=image_path
#     )

#     return RedirectResponse("/profile", status_code=302)

@app.get("/profile")
def profile_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/login")
    payload = verify_token(token)
    if not payload:
        return RedirectResponse("/login")
    user_id = payload["user_id"]

    profile = get_user_profile(user_id)
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "profile": profile}  # pass profile data to template
    )


@app.post("/profile")
def update_profile(
    request: Request,
    full_name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    location: str = Form(None),
    profile_image: UploadFile = File(None)
):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/login")
    payload = verify_token(token)
    if not payload:
        return RedirectResponse("/login")
    user_id = payload["user_id"]

    image_path = None
    if profile_image:
        upload_dir = "static/uploads/"
        os.makedirs(upload_dir, exist_ok=True)
        file_location = os.path.join(upload_dir, profile_image.filename)
        with open(file_location, "wb") as f:
            f.write(profile_image.file.read())
        image_path = file_location

    # Update all fields
    profile = update_user_profile(
        user_id=user_id,
        full_name=full_name,
        email=email,
        phone=phone,
        location=location,
        profile_image=image_path
    )

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "profile_image": profile["profile_image"],
            "full_name": profile["full_name"],
            "email": profile["email"],
            "phone": profile["phone"],
            "location": profile["location"],
            "message": "Profile updated successfully!"
        }
    )