from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

from crud import (
    create_user, get_user_by_email, get_user_profile, update_user_profile,
    get_education, add_education, update_education, get_courses_by_degree,
    get_degrees, get_institutes_by_course, delete_education,
    get_experience_types, get_job_titles, add_experience, get_experience,
    update_experience, delete_experience, add_certification,
    get_certifications, update_certification, delete_certification,
    get_selected_job_titles, save_job_title_selection, delete_job_title_selection
)
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
    redirect_uri =GOOGLE_REDIRECT_URI
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
@app.get("/")
def root(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse("/login")

    payload = verify_token(token)

    if not payload:
        return RedirectResponse("/login")

    return RedirectResponse("/index")
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
@app.get("/education_detail")
def education_page(request: Request):

    token = request.cookies.get("access_token")
    payload = verify_token(token)

    if not payload:
        return RedirectResponse("/login")

    user_id = payload["user_id"]

    education_list =get_education(user_id)
    experience_list = get_experience(user_id)
    certification_list = get_certifications(user_id)
    degrees = get_degrees()
    exp_types = get_experience_types()
    job_titles = get_job_titles()
    selected_job_titles = get_selected_job_titles(user_id)

    return templates.TemplateResponse(
        "education_detail.html",
        {
            "request": request,
            "education_list": education_list,
            "experience_list": experience_list,
            "certification_list": certification_list,
            "selected_job_titles": selected_job_titles,
            "degrees":degrees,
            "exp_types": exp_types,
            "job_titles": job_titles
        
        }
    )
@app.get("/get_courses/{degree_id}")
def get_courses(degree_id: int):
    return get_courses_by_degree(degree_id)

@app.get("/get_institutes/{course_id}")
def get_institutes(course_id: int):
    return get_institutes_by_course(course_id)

@app.post("/education_detail")
def add_educations(
    request: Request,
    degree: int = Form(...),
    course: int = Form(...),
    institution: int = Form(...),
    start_year: str = Form(...),
    end_year: str = Form(...),
    grade: str = Form(...),
    edu_id: int = Form(None)
):
    token = request.cookies.get("access_token")
    payload = verify_token(token)

    if not payload:
        return RedirectResponse("/login")

    user_id = payload["user_id"]

    if edu_id:
        update_education(
            edu_id, degree, course, institution,
            start_year, end_year, grade
        )
    else:
        add_education(
            user_id, degree, course, institution,
            start_year, end_year, grade
        )

    if edu_id:
        return RedirectResponse("/education_detail?type=education&action=updated", status_code=303)
    else:
        return RedirectResponse("/education_detail?type=education&action=added", status_code=303)
@app.post("/delete-education/{edu_id}")
def delete_education_route(request: Request, edu_id: int):

    token = request.cookies.get("access_token")
    payload = verify_token(token)

    if not payload:
        return RedirectResponse("/login")

    user_id = payload["user_id"]
    delete_education(edu_id, user_id)

    return RedirectResponse("/education_detail?type=education&action=deleted", status_code=303)

@app.post("/add-experience")
def add_experience_route(
    request: Request,
    experience_type: int = Form(...),
    job_title: str = Form(...),
    custom_job_title: str = Form(None),
    company_name: str = Form(...),
    start_year: str = Form(...),
    end_year: str = Form(None),
    current_job: str = Form(None),
    responsibilities: str = Form(None),
    exp_id: int = Form(None)
):
    token = request.cookies.get("access_token")
    payload = verify_token(token)

    if not payload:
        return RedirectResponse("/login")

    user_id = payload["user_id"]
    current_job_value = 1 if current_job else 0

    if current_job_value == 1:
        end_year = None

    if job_title == "other":
        job_title_id = None
        final_custom_job_title = custom_job_title
    else:
        job_title_id = int(job_title)
        final_custom_job_title = None

    if exp_id:
        update_experience(
            exp_id, experience_type, job_title_id, final_custom_job_title,
            company_name, start_year, end_year, current_job_value, responsibilities
        )
    else:
        add_experience(
            user_id, experience_type, job_title_id, final_custom_job_title,
            company_name, start_year, end_year, current_job_value, responsibilities
        )

    if exp_id:
        return RedirectResponse("/education_detail?type=experience&action=updated", status_code=303)
    else:
        return RedirectResponse("/education_detail?type=experience&action=added", status_code=303)

@app.post("/delete-experience/{exp_id}")
def delete_experience_route(request: Request, exp_id: int):
    token = request.cookies.get("access_token")
    payload = verify_token(token)

    if not payload:
        return RedirectResponse("/login")

    user_id = payload["user_id"]
    delete_experience(exp_id, user_id)

    return RedirectResponse("/education_detail?type=experience&action=deleted", status_code=303)

@app.post("/add-certification")
def add_certification_route(
    request: Request,
    certification_name: str = Form(...),
    organization: str = Form(...),
    cert_date: str = Form(...),
    cert_id: int = Form(None)
):
    token = request.cookies.get("access_token")
    payload = verify_token(token)

    if not payload:
        return RedirectResponse("/login", status_code=303)

    user_id = payload["user_id"]

    if cert_id:
        update_certification(cert_id, certification_name, organization, cert_date)
    else:
        add_certification(user_id, certification_name, organization, cert_date)

    if cert_id:
        return RedirectResponse("/education_detail?type=certification&action=updated", status_code=303)
    else:
        return RedirectResponse("/education_detail?type=certification&action=added", status_code=303)

@app.post("/delete-certification/{cert_id}")
def delete_certification_route(request: Request, cert_id: int):
    token = request.cookies.get("access_token")
    payload = verify_token(token)

    if not payload:
        return RedirectResponse("/login", status_code=303)

    user_id = payload["user_id"]
    delete_certification(cert_id, user_id)

    return RedirectResponse("/education_detail?type=certification&action=deleted", status_code=303)

@app.post("/save-job-title-selection")
def save_job_title_route(
    request: Request,
    job_title_id: str = Form(...),
    custom_job_title: str = Form(None),
    role_selection_id: int = Form(None)
):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse("/login", status_code=303)

    payload = verify_token(token)
    if not payload:
        return RedirectResponse("/login", status_code=303)

    user_id = payload["user_id"]

    if job_title_id == "other":
        if not custom_job_title or not custom_job_title.strip():
            return RedirectResponse("/education_detail?type=jobrole&action=invalid", status_code=303)

        final_job_title_id = None
        final_custom_job_title = custom_job_title.strip()
    else:
        final_job_title_id = int(job_title_id)
        final_custom_job_title = None

    save_job_title_selection(
        user_id=user_id,
        job_title_id=final_job_title_id,
        custom_job_title=final_custom_job_title,
        role_selection_id=role_selection_id
    )

    if role_selection_id:
        return RedirectResponse("/education_detail?type=jobrole&action=updated", status_code=303)

    return RedirectResponse("/education_detail?type=jobrole&action=added", status_code=303)
@app.post("/delete-job-title-selection/{role_selection_id}")
def delete_job_title_route(request: Request, role_selection_id: int):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse("/login", status_code=303)

    payload = verify_token(token)
    if not payload:
        return RedirectResponse("/login", status_code=303)

    user_id = payload["user_id"]

    delete_job_title_selection(role_selection_id, user_id)

    return RedirectResponse("/education_detail?type=jobrole&action=deleted", status_code=303)