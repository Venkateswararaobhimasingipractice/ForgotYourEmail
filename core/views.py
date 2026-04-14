from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def custom_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Get all users with the same email, ordered by date_joined (oldest first)
            users = User.objects.filter(email=email).order_by('date_joined')

            if users.exists():
                # Pick the first user (oldest)
                user = users.first()

                # Authenticate the user using username and password
                user = authenticate(request, username=user.username, password=password)

                if user:
                    login(request, user)
                    return redirect('home')
                else:
                    return render(request, 'core/login.html', {'error': 'Invalid Credentials'})
            else:
                return render(request, 'core/login.html', {'error': 'User not found. Please Register'})

        except User.DoesNotExist:
            return render(request, 'core/login.html', {'error': 'User not found. Please Register'})

    return render(request, 'core/login.html')


from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

def custom_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=email, password=password)

            # Important fix here:
            user.backend = 'django.contrib.auth.backends.ModelBackend'

            login(request, user)
            return redirect('home')
        else:
            # Username already exists
            return render(request, 'core/register.html', {'error': 'Username already exists.'})

    return render(request, 'core/register.html')



def home(request):
    return render(request, 'core/home1.html')

def custom_logout(request):
    logout(request)
    return redirect('login')


def privacy_policy(request):
    return render(request, 'core/privacy-policy.html')

def terms_of_service(request):
    return render(request, 'core/terms.html')

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import AppUser, UserProfile

import traceback

'''@csrf_exempt
def register_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("📩 Payload received:", data)

            uid = data.get("uid")
            email = data.get("email")
            login_type = data.get("type", "manual")
            google_id = data.get("google_id")
            refresh_token = data.get("refresh_token")

            if not uid or not email:
                return JsonResponse({"error": "UID and email are required"}, status=400)

            user, created = AppUser.objects.get_or_create(
                firebase_uid=uid,
                defaults={
                    "email": email,
                    "type": login_type,
                    "google_id": google_id,
                    "refresh_token": refresh_token,
                }
            )

            if not created and login_type == "link":
                user.type = "link"
                if google_id:
                    user.google_id = google_id
                if refresh_token:
                    user.refresh_token = refresh_token
                user.save()

            # 👇 Add profile creation with logging
            profile, p_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "name": email,
                    "phone": "0000000000",
                    "profile_image_url": "https://i.imgur.com/7suwDp5.jpeg"
                }
            )
            print(f"✅ Profile {'created' if p_created else 'exists'} for {email}")

            return JsonResponse(
                {"message": "User registered" if created else "User already exists"},
                status=201 if created else 200
            )

        except Exception as e:
            print("🔥 Exception during register_user:")
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)'''


@csrf_exempt
def login_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        uid = data.get("uid")
        email = data.get("email", None)
        google_id = data.get("google_id", None)
        refresh_token = data.get("refresh_token", None)
             #put("fcm_token", fcmToken)
        fcmToken=data.get("fcm_token")

        try:
            user = AppUser.objects.get(firebase_uid=uid)

            # Optional: update Google info if provided
            if google_id:
                user.google_id = google_id
            if refresh_token:
                user.refresh_token = refresh_token
            user.login=True
            user.fcm_token=fcmToken
            user.save()

            return JsonResponse({"message": "Login success"}, status=200)

        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import AppUser, UserProfile
from django.conf import settings
import json
import requests

def upload_to_imgur(image_file):
    url = "https://api.imgur.com/3/image"
    headers = {
        "Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}"
    }

    try:
        response = requests.post(url, headers=headers, files={"image": image_file})
        response.raise_for_status()

        data = response.json()
        if data.get('success'):
            return data['data']['link']
        else:
            raise Exception("Imgur API failed")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Imgur upload failed: {str(e)}")


@csrf_exempt
def save_profile(request):
    if request.method == "POST":
        uid = request.POST.get("uid")
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        image = request.FILES.get("profile_image_url")  # Optional

        try:
            app_user, _ = AppUser.objects.get_or_create(firebase_uid=uid, defaults={"email": email})
            profile, _ = UserProfile.objects.get_or_create(user=app_user)

            profile.name = name
            profile.phone = phone

            if image:
                imgur_url = upload_to_imgur(image)
                profile.profile_image_url = imgur_url

            profile.save()

            return JsonResponse({
                "message": "Profile saved successfully",
                "image_url": profile.profile_image_url
            })

        except Exception as e:
            return JsonResponse({"error": f"Exception in save_profile: {str(e)}"}, status=500)

@csrf_exempt
def get_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)
        uid = data.get("uid")

        try:
            app_user = AppUser.objects.get(firebase_uid=uid)
            profile = UserProfile.objects.get(user=app_user)

            return JsonResponse({
                "name": profile.name,
                "phone": profile.phone,
                "profile_image_url": profile.profile_image_url or "https://i.imgur.com/7suwDp5.jpeg",
                "type": app_user.type  # ✅ include this
            })

        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        except UserProfile.DoesNotExist:
            return JsonResponse({
                "name": "bot",
                "phone": "",
                "profile_image_url": "https://i.imgur.com/7suwDp5.jpeg",
                "type": app_user.type  # return even if profile is missing
            })


@csrf_exempt
def check_type(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()  # 👈 force lowercase
        try:
            user = AppUser.objects.get(email=email)
            return JsonResponse({"type": user.type}, status=200)
        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)


@csrf_exempt
def updatetype(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()  # 👈 normalize
        try:
            user = AppUser.objects.get(email=email)
            user.type = "link"
            user.save()
            return JsonResponse({"message": "User type updated to link"}, status=200)
        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)



GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import AppUser

@csrf_exempt
def link_google_account(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        print("📩 Payload received:", data)

        firebase_uid = data.get("uid")
        email = data.get("email")
        google_id = data.get("google_id")
        auth_code = data.get("refresh_token")  # Actually the serverAuthCode

        if not (firebase_uid and email and google_id and auth_code):
            return JsonResponse({"error": "Missing fields"}, status=400)

        try:
            user = AppUser.objects.get(firebase_uid=firebase_uid, email=email)
        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        # 🔁 Exchange serverAuthCode for access & refresh tokens
        try:
            response = requests.post("https://oauth2.googleapis.com/token", data={
                "code": auth_code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": "",  # empty for Android clients
                "grant_type": "authorization_code"
            })

            if response.status_code != 200:
                return JsonResponse({"error": "Failed to exchange code", "details": response.json()}, status=400)

            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")  # Might be None if already granted
            expires_in = token_data.get("expires_in", 3600)
            token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": f"Token exchange failed: {str(e)}"}, status=500)

        # ✅ Save to user
        user.google_id = google_id
        if refresh_token:
            user.refresh_token = refresh_token
        user.access_token = access_token
        user.token_expiry = token_expiry
        user.type = "link"
        user.save()

        print(f"✅ Linked Google account for: {email}")
        return JsonResponse({"message": "Google account linked successfully"})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


# views.py

import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AppUser

# Helper function to refresh access token
def refresh_google_access_token(refresh_token: str):
    response = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    })

    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)
        expiry_time = datetime.now() + timedelta(seconds=expires_in)
        return access_token, expiry_time
    else:
        raise Exception(f"Failed to refresh token: {response.text}")

# API to get valid access token
@api_view(["POST"])
def get_valid_access_token(request):
    firebase_uid = request.data.get("uid")

    try:
        user = AppUser.objects.get(firebase_uid=firebase_uid)

        if not user.access_token or not user.token_expiry or user.token_expiry <= now():
            access_token, expiry = refresh_google_access_token(user.refresh_token)
            user.access_token = access_token
            user.token_expiry = expiry
            user.save()

        return Response({"access_token": user.access_token})

    except AppUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

def p22(request):
    return render(request, 'core/google9b73a2ec9b048a6e.html')

import json
import traceback
import requests
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .models import AppUser, UserProfile

def exchange_auth_code_for_tokens(auth_code):
    response = requests.post("https://oauth2.googleapis.com/token", data={
        "code": auth_code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": "",  # Leave empty for Android apps
        "grant_type": "authorization_code"
    })

    if response.status_code == 200:
        data = response.json()
        return {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),  # May be None if reused
            "expires_in": data.get("expires_in", 3600)
        }
    else:
        raise Exception(f"Token exchange failed: {response.text}")


@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        print("📩 Payload received:", data)

        uid = data.get("uid")
        email = data.get("email")
        login_type = data.get("type", "manual")
        google_id = data.get("google_id")
        auth_code = data.get("refresh_token")  # serverAuthCode misnamed

        if not uid or not email:
            return JsonResponse({"error": "UID and email are required"}, status=400)

        # Initialize token fields
        access_token = None
        token_expiry = None
        refresh_token = None
        fcm_token = None

        if login_type == "google" and auth_code:
            try:
                token_data = exchange_auth_code_for_tokens(auth_code)
                access_token = token_data["access_token"]
                refresh_token = token_data.get("refresh_token")  # May be None if user already authorized
                expires_in = token_data["expires_in"]
                token_expiry = datetime.now() + timedelta(seconds=expires_in)
                fcm_token = data.get("fcm_token")
            except Exception as e:
                print("🔥 Error exchanging auth code:")
                traceback.print_exc()
                return JsonResponse({"error": f"Failed to get tokens: {str(e)}"}, status=400)

        user, created = AppUser.objects.get_or_create(
            firebase_uid=uid,
            defaults={
                "email": email,
                "type": login_type,
                "google_id": google_id,
                "refresh_token": refresh_token,
                "access_token": access_token,
                "token_expiry": token_expiry,
                "fcm_token": fcm_token,
            }
        )

        if not created and login_type == "link":
            user.type = "link"
            if google_id:
                user.google_id = google_id
            if refresh_token:
                user.refresh_token = refresh_token
            if access_token:
                user.access_token = access_token
                user.token_expiry = token_expiry
            if fcm_token:
                user.fcm_token = fcm_token
            user.save()

        # Create user profile
        profile, p_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "name": email,
                "phone": "0000000000",
                "profile_image_url": "https://i.imgur.com/7suwDp5.jpeg"
            }
        )
        print(f"✅ Profile {'created' if p_created else 'exists'} for {email}")

        return JsonResponse(
            {"message": "User registered" if created else "User already exists"},
            status=201 if created else 200
        )

    except Exception as e:
        print("🔥 Exception during register_user:")
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
    
# views.py
import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AppUser

GOOGLE_TOKEN_ENDPOINT = ""
#ANOTHER_PROJECT_URL = "https://mysupportgoogledjango.vercel.app/token_expired/"

@csrf_exempt
def refresh_all_access_tokens(request):
    users_with_refresh = AppUser.objects.filter(refresh_token__isnull=False)
    total = users_with_refresh.count()
    success_count = 0
    expired_users = []

    for user in users_with_refresh:
        try:
            response = requests.post(GOOGLE_TOKEN_ENDPOINT, data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": user.refresh_token,
                "grant_type": "refresh_token"
            })

            if response.status_code == 200:
                token_data = response.json()
                user.access_token = token_data["access_token"]
                user.token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"])
                user.save()
                success_count += 1
            else:
                # ❌ Mark user as logged out
                user.login = False
                user.save()
                expired_users.append({
                    "firebase_uid": user.firebase_uid,
                    "fcm_token": user.fcm_token,
                    "email": user.email
                })

        except Exception as e:
            print(f"Error for user {user.firebase_uid}: {e}")
            user.login = False
            user.save()
            expired_users.append({
                "firebase_uid": user.firebase_uid,
                "fcm_token": user.fcm_token,
                "email": user.email
            })
    print(expired_users)
    # Notify Project B
    if expired_users:
        try:
            requests.post(f"https://mysupportgoogledjango.vercel.app/token_expired/", json={"users": expired_users}, timeout=30)
            print("val")
        except Exception as e:
            print(f"❌ Failed to notify Project B: {e}")

    return JsonResponse({
        "total": total,
        "success": success_count,
        "expired": len(expired_users)
    })



from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import requests
from core.models import AppUser  # adjust if your model is elsewhere
import os

@api_view(["POST"])
def get_access_token(request):
    try:
        uid = request.data.get("uid")
        if not uid:
            return JsonResponse({"error": "Missing uid"}, status=400)

        user = AppUser.objects.get(firebase_uid=uid)
        now = timezone.now()

        # If token is valid, return it
        if user.access_token and user.token_expiry and user.token_expiry > now:
            return JsonResponse({"access_token": user.access_token})

        # Else regenerate token
        refresh_token = user.refresh_token
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(token_url, data=payload)
        if response.status_code != 200:
            return JsonResponse({"error": "Failed to refresh token"}, status=400)

        token_data = response.json()
        access_token = token_data["access_token"]
        expires_in = token_data["expires_in"]

        # Update user record
        user.access_token = access_token
        user.token_expiry = now + timedelta(seconds=expires_in - 60)  # small buffer
        user.save()

        return JsonResponse({"access_token": access_token})

    except AppUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)





import json
import requests
from rest_framework.decorators import api_view
from django.http import JsonResponse
from core.models import AppUser,EmailAction,TodoTask
from django.views.decorators.csrf import csrf_exempt


# --- 🔹 Gemini API ---
GEMINI_API_KEY = ""
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"





# --- 🔹 Get Join Date API ---
@api_view(["POST"])
@csrf_exempt
def get_join_date(request):
    uid = request.data.get("uid")
    if not uid:
        return JsonResponse({"error": "Missing uid"}, status=400)

    try:
        user = AppUser.objects.get(firebase_uid=uid)
        return JsonResponse({"date_joined": user.date_joined.isoformat()})
    except AppUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)



@api_view(['POST'])
def user_action(request):
    data = request.data
    action = data.get("action")
    ea = EmailAction.objects.create(
        user=request.user,
        email_id=data.get("email_id"),
        subject=data.get("subject", ""),
        action=action
    )
    return Response({"status": "ok", "id": ea.id})


@api_view(['POST'])
def add_todo(request):
    data = request.data
    task = TodoTask.objects.create(
        user=request.user,
        email_id=data.get("email_id", ""),
        title=data["task"]
    )
    return Response({"id": task.id, "title": task.title, "status": task.status})


@api_view(['POST'])
def mark_todo_done(request):
    task_id = request.data.get("task_id")
    task = TodoTask.objects.filter(id=task_id, user=request.user).first()
    if not task:
        return Response({"error": "not found"}, 404)
    task.status = "done"
    task.save()
    return Response({"status": "updated"})


@api_view(['POST'])
def delete_todo(request):
    task_id = request.data.get("task_id")
    task = TodoTask.objects.filter(id=task_id, user=request.user).first()
    if not task:
        return Response({"error": "not found"}, 404)
    task.delete()
    return Response({"status": "deleted"})


@api_view(['POST'])
def update_todo(request):
    task_id = request.data.get("task_id")
    task = TodoTask.objects.filter(id=task_id, user=request.user).first()
    if not task:
        return Response({"error": "not found"}, 404)
    task.title = request.data.get("title", task.title)
    task.save()
    return Response({"status": "updated"})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TodoTask, AppUser  # AppUser stores firebase_uid
from django.contrib.auth.models import User

@csrf_exempt
def get_todos(request):
    if request.method == "GET":
        uid = request.GET.get("uid")
        if not uid:
            return JsonResponse({"error": "UID is required"}, status=400)

        try:
            app_user = AppUser.objects.get(firebase_uid=uid)
            user = app_user.user  # Assuming AppUser is linked to Django User
        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        todos = TodoTask.objects.filter(user=user, status="pending").order_by("-created_at")

        data = [
            {
                "id": todo.id,
                "title": todo.title,
                "email_id": todo.email_id,
                "status": todo.status,
                "created_at": todo.created_at.isoformat()
            }
            for todo in todos
        ]

        return JsonResponse({"todos": data}, status=200)
    return JsonResponse({"error": "Invalid request"}, status=405)


import json
import requests
from email.mime.text import MIMEText
import base64
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AppUser




import json
from django.utils import timezone
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ScheduledTask, AppUser

GOOGLE_CAL_CREATE_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

def create_calendar_event(access_token, title, when):
    start = when.isoformat()
    end = (when + timezone.timedelta(hours=1)).isoformat()
    event = {"summary": title, "start": {"dateTime": start}, "end": {"dateTime": end}}
    resp = requests.post(GOOGLE_CAL_CREATE_URL,
                         headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                         json=event)
    return resp.json().get("id", "")

@api_view(['GET'])
def get_schedules(request):
    uid = request.GET.get("uid")
    user = AppUser.objects.get(firebase_uid=uid).user
    tasks = ScheduledTask.objects.filter(user=user)
    data = [{"id": t.id, "title": t.title, "time": t.scheduled_time, "done": t.is_done} for t in tasks]
    return Response(data)

@api_view(['POST'])
def add_schedule_api(request):
    data = json.loads(request.body)
    uid, email_id, title, ts = data.get("uid"), data.get("email_id"), data.get("title"), data.get("time")
    when = timezone.datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    user = AppUser.objects.get(firebase_uid=uid).user
    access_token = AppUser.objects.get(firebase_uid=uid).access_token
    event_id = create_calendar_event(access_token, title, when)
    st = ScheduledTask.objects.create(user=user, email_id=email_id, title=title, scheduled_time=when, calendar_event_id=event_id)
    return Response({"id": st.id})

@api_view(['POST'])
def update_schedule_api(request):
    data = json.loads(request.body)
    st = ScheduledTask.objects.get(id=data["id"], user=AppUser.objects.get(firebase_uid=data["uid"]).user)
    st.title = data.get("title", st.title)
    if "time" in data:
        when = timezone.datetime.fromtimestamp(data["time"] / 1000, tz=timezone.utc)
        st.scheduled_time = when
    st.save()
    return Response({"status": "updated"})

@api_view(['POST'])
def delete_schedule_api(request):
    data = json.loads(request.body)
    st = ScheduledTask.objects.get(id=data["id"], user=AppUser.objects.get(firebase_uid=data["uid"]).user)
    st.delete()
    return Response({"status": "deleted"})

from django.utils import timezone


def mark_due_tasks_done():
    now = timezone.now()
    ScheduledTask.objects.filter(scheduled_time__lt=now, is_done=False).update(is_done=True)




"new version new split methods"
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import AppUser,EmailClassification,IgnoredEmail
import requests
import json
#ANOTHER_PROJECT_URL = "http://127.0.0.1:8000/sync_and_notify_users/"
#ANOTHER_PROJECT_URL5 = "http://127.0.0.1:8000/sync_and_notify_users5/"
ANOTHER_PROJECT_URL = "https://mysupportgoogledjango.vercel.app/sync_and_notify_users/"
ANOTHER_PROJECT_URL5 = "https://mysupportgoogledjango.vercel.app/sync_and_notify_users5/"
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time
import pytz
import json
import requests


@csrf_exempt
def sync_and_notify_users(request):
    try:
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)

        # ✅ Restrict execution to 9:30 AM – 10:00 PM
        start_time = time(9, 30)
        end_time = time(22, 0)
        if not (start_time <= now.time() <= end_time):
            return JsonResponse({"status": "outside allowed time window"}, status=200)

        today = now.date()

        # ✅ Get all logged-in users
        users = AppUser.objects.filter(login=True)

        # Prepare a list with only **one user whose last_notified_date != today**
        users_to_sync = []
        for user in users:
            if user.last_notified_date != today:
                user.last_notified_date = today
                user.save()
                users_to_sync.append(user)
                break  # process only one user per call

        if not users_to_sync:
            return JsonResponse({"status": "no users to sync today"})

        # Prepare user list for sending
        user_data_list = []
        for user in users_to_sync:
            ignored_emails_qs = IgnoredEmail.objects.filter(user=user, count__gt=19)
            ignored_list = [ie.ignored_email for ie in ignored_emails_qs]
            user_data_list.append({
                "firebase_uid": user.firebase_uid,
                "email": user.email,
                "access_token": user.access_token,
                "refresh_token": user.refresh_token,
                "date_joined": int(user.date_joined.timestamp()),
                "fcm_token": user.fcm_token,
                "ignored_list": ignored_list
            })

        # Prepare classification list
        emails = EmailClassification.objects.all()
        email_data_list = []
        for email in emails:
            email_data_list.append({
                "uid": email.uid,
                "email_id": email.email_id,  # unique ID
                "classification": email.classification,
                "created_at": int(email.created_at.timestamp())
            })

        # ✅ Send to another project
        res = requests.post(
            ANOTHER_PROJECT_URL,
            json={"users": user_data_list, "classificationlist": email_data_list},
            timeout=60
        )

        # ✅ Update last_notified_date for the synced user
        

        return JsonResponse(res.json(), status=res.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
def sync_and_notify_users5(request):
    try:
        # ✅ Get all logged-in users from current project's DB
        users = AppUser.objects.filter(login=True)

        # Prepare a simple list of user info to send
        user_data_list = []
        for user in users:
            ignored_emails_qs = IgnoredEmail.objects.filter(user=user, count__gt=19)
            ignored_list = [ie.ignored_email for ie in ignored_emails_qs]
            user_data_list.append({
                "firebase_uid": user.firebase_uid,
                "email": user.email,
                "access_token": user.access_token,
                "refresh_token": user.refresh_token,
                "date_joined": int(user.date_joined.timestamp()),
                "fcm_token": user.fcm_token,
                "ignored_list": ignored_list,
            })
        emails = EmailClassification.objects.all()

        email_data_list = []
        for email in emails:
            email_data_list.append({
                "uid": email.uid,
                "email_id": email.email_id,  # unique ID, not email address
                "classification": email.classification,
                "created_at": int(email.created_at.timestamp())
            })

        # ✅ Send to another project
        res = requests.post(
            ANOTHER_PROJECT_URL5,
            json={"users": user_data_list,"classificationlist":email_data_list},
            timeout=60
        )

        return JsonResponse(res.json(), status=res.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def store_classification(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email_id = data.get("email_id")
            uid = data.get("uid")
            classification = data.get("classification")
            

            # Create or update the EmailClassification record
            obj, created = EmailClassification.objects.get_or_create(
                email_id=email_id,
                defaults={
                    "uid": uid,
                    "classification": classification,
                   
                },
            )

            if not created:
                obj.classification = classification
             
                obj.save()

            return JsonResponse({"status": "stored", "created": created})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)

# views.py (Current Project)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import AppUser, UserProfile
import requests, json

GMAIL_SERVICE_BASE = "https://mysupportgoogledjango.vercel.app"

@csrf_exempt
def generate_reply_from_email(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        uid = data.get("uid")
        email_id = data.get("email_id","")
        requirements = data.get("requirements", "")
        suggestions = data.get("suggestions", "")
        manual=data.get("manual","")
        sender=data.get("sender","")

        if not uid :
            return JsonResponse({"error": "Missing uid"}, status=400)

        # ✅ DB fetch in current project
        user = AppUser.objects.get(firebase_uid=uid)
        user_profile = UserProfile.objects.get(user=user)

        # Prepare payload for Gmail Service
        payload = {
            "access_token": user.access_token,
            "refresh_token": user.refresh_token,
            "email_id": email_id,
            "requirements": requirements,
            "suggestions": suggestions,
            "user_name": user_profile.name,
            "user_email": user.email,
            "manual": manual,
            "sender": sender
        }

        # Forward to Gmail Service
        resp = requests.post(f"https://mysupportgoogledjango.vercel.app/generate_reply/", json=payload)
        return JsonResponse(resp.json(), status=resp.status_code)

    except AppUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def send_auto_reply(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        sender_email = data.get("sender_email")
        subject = data.get("subject")
        content = data.get("reply")
        user_email = data.get("user_email")

        if not all([sender_email, subject, content, user_email]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # ✅ DB fetch in current project
        user = AppUser.objects.get(email=user_email)

        payload = {
            "access_token": user.access_token,
            "refresh_token": user.refresh_token,
            "sender_email": sender_email,
            "subject": subject,
            "content": content,
            "from_email": user.email
        }

        resp = requests.post(f"{GMAIL_SERVICE_BASE}/send_reply/", json=payload)
        return JsonResponse(resp.json(), status=resp.status_code)

    except AppUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
import json
import requests
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from .models import AppUser, ScheduledTask

GOOGLE_API_BASE = "https://mysupportgoogledjango.vercel.app"  # other project


def send_to_google_calendar(user, task):
    """
    Sends the task to another project that handles Google Calendar integration.
    """
    try:
        payload = {
            "google_id": user.google_id,
            "access_token": user.access_token,
            "refresh_token": user.refresh_token,
            "token_expiry": user.token_expiry.isoformat() if user.token_expiry else None,
            "title": task.title,
            "description": task.description,
            "scheduled_time": task.scheduled_time.isoformat(),
            "email_subject": task.email_subject,
            "email_body": task.email_body,
        }
        response = requests.post(f"https://mysupportgoogledjango.vercel.app/add_to_calendar/", json=payload)
        #response = requests.post(f"http://127.0.0.1:8000/add_to_calendar/", json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


from django.utils.timezone import make_aware
import pytz

@csrf_exempt
def add_schedule(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = get_object_or_404(AppUser, firebase_uid=data["uid"])

            scheduled_time = parse_datetime(data["scheduled_time"])
            if scheduled_time is None:
                return JsonResponse({"error": "Invalid datetime format"}, status=400)

            # Ensure the datetime is timezone aware (Asia/Kolkata)
            if scheduled_time.tzinfo is None:
                kolkata_tz = pytz.timezone("Asia/Kolkata")
                scheduled_time = make_aware(scheduled_time, kolkata_tz)

            task = ScheduledTask.objects.create(
                user=user,
                title=data["title"],
                description=data.get("description", ""),
                schedule_type=data.get("type", "email"),
                scheduled_time=scheduled_time,
                recipient_email=data.get("recipient_email"),
                email_subject=data.get("email_subject"),
                email_body=data.get("email_body"),
            )

            if task.schedule_type == "calendar":
                google_response = send_to_google_calendar(user, task)
                if google_response.get("status") == "success":
                    task.google_event_id = google_response.get("event_id")
                    task.google_event_link = google_response.get("htmlLink")
                    task.save(update_fields=["google_event_id", "google_event_link"])
                return JsonResponse({
                    "status": "ok",
                    "id": task.id,
                    "google_result": google_response
                })

            return JsonResponse({"status": "ok", "id": task.id})

        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)

import json
import requests
from django.utils import timezone
from .models import ScheduledTask

EMAIL_API_URL = "https://mysupportgoogledjango.vercel.app/send_reply/"  

def process_due_emails():
    """
    Finds all due email tasks, sends them to the other project,
    and marks them as done if successful.
    """
    due_tasks = ScheduledTask.objects.filter(
        schedule_type="email",
        done=False,
        scheduled_time__lte=timezone.now()
    )

    for task in due_tasks:
        user = task.user
        payload = {
            "access_token": user.access_token,
            "refresh_token": user.refresh_token,
            "from_email": user.email,  # Sender is the logged-in user
            "sender_email": task.recipient_email,  # Recipient from task
            "subject": task.email_subject,
            "content": task.email_body
        }

        try:
            resp = requests.post(EMAIL_API_URL, json=payload, timeout=10)
            result = resp.json()

            if resp.status_code == 200 and "error" not in result:
                task.done = True
                task.save(update_fields=["done"])
                print(f"✅ Email sent for task {task.id}")
            else:
                print(f"❌ Failed to send task {task.id}: {result}")

        except Exception as e:
            print(f"⚠️ Exception sending task {task.id}: {e}")

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive, now
from datetime import timedelta
import pytz
import json
import requests

@csrf_exempt
def update_schedule(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        uid = data.get("uid")
        schedule_id = data.get("id")

        if not uid or not schedule_id:
            return JsonResponse({"error": "uid and id are required"}, status=400)

        # Fetch user and task
        user = get_object_or_404(AppUser, firebase_uid=uid)
        task = get_object_or_404(ScheduledTask, id=schedule_id, user=user)

        # Update only provided fields
        if "title" in data:
            task.title = data["title"]
        if  "sender" in data:
            task.recipient_email = data["sender"]

        if "description" in data:
            task.description = data["description"]

        if "email_subject" in data:
            task.email_subject = data["email_subject"]

        if "email_body" in data:
            task.email_body = data["email_body"]

        if "scheduled_time" in data:
            scheduled_time = parse_datetime(data["scheduled_time"])
            if scheduled_time is None:
                return JsonResponse({"error": "Invalid datetime format"}, status=400)

            # Ensure timezone-aware
            if is_naive(scheduled_time):
                scheduled_time = make_aware(scheduled_time, pytz.timezone("Asia/Kolkata"))

            # Store in UTC internally
            task.scheduled_time = scheduled_time.astimezone(pytz.UTC)

        if "type" in data:
            task.schedule_type = data["type"]

        task.save()

        # If Google Calendar event, update in other project
        if task.schedule_type == "calendar" and task.google_event_id:
            google_update_url = "https://mysupportgoogledjango.vercel.app/update_google_event/"

            # Ensure token_expiry is aware
            if user.token_expiry and is_naive(user.token_expiry):
                user.token_expiry = make_aware(user.token_expiry, pytz.UTC)

            # Check token expiry (refresh if needed)
            if not user.token_expiry or user.token_expiry <= now():
                return JsonResponse({"error": "Google token expired. Please re-authenticate."}, status=401)

            kolkata_time = task.scheduled_time.astimezone(pytz.timezone("Asia/Kolkata"))
            payload = {
                "google_event_id": task.google_event_id,
                "title": task.title,
                "description": task.description,
                "scheduled_time": kolkata_time.isoformat(),
                "access_token": user.access_token,
                "refresh_token": user.refresh_token,
                "token_expiry": user.token_expiry.isoformat()
            }
            try:
                r = requests.post(google_update_url, json=payload)
                google_response = r.json()

                if google_response.get("status") == "success":
                    task.google_event_link = google_response.get("htmlLink", task.google_event_link)
                    task.save(update_fields=["google_event_link"])
                else:
                    return JsonResponse({"error": "Google update failed", "details": google_response}, status=500)

            except Exception as e:
                return JsonResponse({"error": f"Failed to update Google event: {str(e)}"}, status=500)

        return JsonResponse({"status": "ok", "id": task.id})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
import requests

GOOGLE_API_BASE = "https://mysupportgoogledjango.vercel.app"  # Support project URL

@csrf_exempt
def delete_schedule(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        uid = data.get("uid")
        schedule_id = data.get("id")

        if not uid or not schedule_id:
            return JsonResponse({"error": "uid and id are required"}, status=400)

        user = get_object_or_404(AppUser, firebase_uid=uid)
        task = get_object_or_404(ScheduledTask, id=schedule_id, user=user)

        print(f"Attempting to delete schedule ID: {schedule_id} for user: {uid}")

        # If it's a calendar event, delete from Google Calendar first
        if task.schedule_type == "calendar" and task.google_event_id:
            token_expiry = user.token_expiry

            # ✅ Make token_expiry timezone-aware if naive
            if token_expiry and is_naive(token_expiry):
                token_expiry = make_aware(token_expiry, timezone=timezone.utc)

            payload = {
                "google_event_id": task.google_event_id,
                "access_token": user.access_token,
                "refresh_token": user.refresh_token,
                "token_expiry": token_expiry.isoformat() if token_expiry else None
            }

            try:
                # Use local or deployed endpoint
                r = requests.post(
                    "https://mysupportgoogledjango.vercel.app/delete_google_event/",
                    json=payload,
                    timeout=10
                )

                if r.status_code != 200:
                    return JsonResponse({
                        "error": "Google Calendar delete failed",
                        "details": r.json()
                    }, status=500)

            except requests.exceptions.ConnectionError as e:
                return JsonResponse({
                    "error": "Failed to connect to Google Calendar service",
                    "details": str(e)
                }, status=500)
            except Exception as e:
                return JsonResponse({
                    "error": f"Google Calendar delete request failed: {str(e)}"
                }, status=500)

        # Finally, delete the task from the database
        task.delete()

        print(f"Successfully deleted schedule ID: {schedule_id}")

        return JsonResponse({"status": "success"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.serializers import serialize
from django.utils.dateparse import parse_datetime
import json
from .models import ScheduledTask, AppUser

from django.utils import timezone

def serialize_schedule(task):
    """
    Convert ScheduledTask instance to dict
    Classifier is calculated ONLY using time
    """
    now = timezone.now()

    classifier = (
        "completed"
        if task.scheduled_time < now
        else "pending"
    )

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "schedule_type": task.schedule_type,
        "scheduled_time": task.scheduled_time.isoformat(),
        "classifier": classifier,   # ✅ time-based
        "recipient_email": task.recipient_email,
        "email_subject": task.email_subject,
        "email_body": task.email_body,
        "google_event_id": task.google_event_id,
        "google_event_link": task.google_event_link,
        "created_at": task.created_at.isoformat(),
        "uid": task.user.firebase_uid,
        "email": task.user.email
    }


@csrf_exempt
def get_pending_schedules(request):
    """Return pending schedules for a given uid or email"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)
    try:
        data = json.loads(request.body)
        uid = data.get("uid")
        email = data.get("email")

        if not uid and not email:
            return JsonResponse({"error": "uid or email is required"}, status=400)

        # Find user by uid or email
        if uid:
            user = get_object_or_404(AppUser, firebase_uid=uid)
        else:
            user = get_object_or_404(AppUser, email=email)

        schedules = ScheduledTask.objects.filter(user=user, done=False).order_by("scheduled_time")
        return JsonResponse({
            "status": "success",
            "pending_schedules": [serialize_schedule(t) for t in schedules]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
@csrf_exempt
def get_all_schedules(request):
    """
    Return ALL schedules for a user (uid or email)
    Each task classified using time only
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        uid = data.get("uid")
        email = data.get("email")

        if not uid and not email:
            return JsonResponse(
                {"error": "uid or email is required"},
                status=400
            )

        # Identify user
        if uid:
            user = get_object_or_404(AppUser, firebase_uid=uid)
        else:
            user = get_object_or_404(AppUser, email=email)

        schedules = ScheduledTask.objects.filter(
            user=user
        ).order_by("-scheduled_time")

        return JsonResponse({
            "status": "success",
            "total": schedules.count(),
            "schedules": [
                serialize_schedule(task) for task in schedules
            ]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def get_completed_schedules(request):
    """Return completed schedules for a given uid or email"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)
    try:
        data = json.loads(request.body)
        uid = data.get("uid")
        email = data.get("email")

        if not uid and not email:
            return JsonResponse({"error": "uid or email is required"}, status=400)

        # Find user by uid or email
        if uid:
            user = get_object_or_404(AppUser, firebase_uid=uid)
        else:
            user = get_object_or_404(AppUser, email=email)

        schedules = ScheduledTask.objects.filter(user=user, done=True).order_by("-scheduled_time")
        return JsonResponse({
            "status": "success",
            "completed_schedules": [serialize_schedule(t) for t in schedules]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Todo
import json

@csrf_exempt
def create_task(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
        uid = data.get("uid")
        title = data.get("title", "").strip()
        if not uid or not title:
            return JsonResponse({"error": "uid and title are required"}, status=400)

        task = Todo.objects.create(user_uid=uid, title=title)
        return JsonResponse({
            "status": "success",
            "task": {
                "id": task.id,
                "title": task.title,
                "created_at": task.created_at.isoformat(),
                "done": task.done
            }
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Todo  # Make sure your Todo model is imported

@csrf_exempt
def get_all_tasks(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8"))
        uid = data.get("uid")
        if not uid:
            return JsonResponse({"error": "uid is required"}, status=400)

        # Fetch all tasks for this user
        qs = Todo.objects.filter(user_uid=uid).order_by("-created_at")
        tasks = list(qs.values("id", "title", "created_at", "done"))

        # Convert datetime to ISO format
        for t in tasks:
            t["created_at"] = t["created_at"].isoformat()

        return JsonResponse({"status": "success", "tasks": tasks})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_tasks(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
        uid = data.get("uid")
        status_filter = (data.get("status") or "pending").lower()  # "pending" or "completed"
        if not uid:
            return JsonResponse({"error": "uid is required"}, status=400)

        done_val = True if status_filter == "completed" else False
        qs = Todo.objects.filter(user_uid=uid, done=done_val).order_by("-created_at")
        tasks = list(qs.values("id", "title", "created_at", "done"))
        # Serialize datetime to isoformat (values() returns datetime objects)
        for t in tasks:
            t["created_at"] = t["created_at"].isoformat()
        return JsonResponse({"status": "success", "tasks": tasks})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_task(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
        task_id = data.get("task_id")
        if not task_id:
            return JsonResponse({"error": "task_id is required"}, status=400)

        task = Todo.objects.get(id=task_id)
        if "title" in data and isinstance(data["title"], str):
            task.title = data["title"].strip() or task.title
        if "done" in data:
            task.done = bool(data["done"])
        task.save()
        return JsonResponse({"status": "success"})
    except Todo.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def delete_task(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
        task_id = data.get("task_id")
        if not task_id:
            return JsonResponse({"error": "task_id is required"}, status=400)
        Todo.objects.filter(id=task_id).delete()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import AppUser

GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"

@csrf_exempt
def handle_auth_code(request):
    """
    Endpoint called from Android when user re-authenticates.
    Request body should include:
    {
      "firebase_uid": "...",
      "auth_code": "..."
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data= json.loads(request.body.decode("utf-8"))
    firebase_uid = data.get("uid")
    auth_code = data.get("auth_code")

    if not firebase_uid or not auth_code:
        return JsonResponse({"error": "Missing firebase_uid or auth_code"}, status=400)

    try:
        # Exchange auth code for tokens
        token_res = requests.post(GOOGLE_TOKEN_ENDPOINT, data={
            "code": auth_code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": "",  # must match Android OAuth config
            "grant_type": "authorization_code",
        })

        if token_res.status_code != 200:
            return JsonResponse({
                "error": "Failed to exchange auth code",
                "details": token_res.json()
            }, status=400)

        token_data = token_res.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")

        # Update DB
        user = AppUser.objects.filter(firebase_uid=firebase_uid).first()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        user.access_token = access_token
        if refresh_token:  # refresh_token may not always be returned if already issued
            user.refresh_token = refresh_token
        user.token_expiry = datetime.now() + timedelta(seconds=expires_in)
        user.login = True  # reactivate login
        user.save()

        return JsonResponse({
            "success": True,
            "firebase_uid": firebase_uid,
            "access_token": access_token,
            "expires_in": expires_in,
            "refresh_token": bool(refresh_token)
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.utils import timezone
from django.db import transaction
import requests
import json

from django.http import JsonResponse
from django.utils import timezone
import requests

def process_due_tasks(request):
    """
    GET endpoint to process due tasks and return JSON results.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    results = []
    due_tasks = ScheduledTask.objects.filter(done=False, scheduled_time__lte=timezone.now())

    for task in due_tasks:
        try:
            if task.schedule_type == "calendar":
                task.done = True
                task.save(update_fields=["done"])
                results.append({
                    "task_id": task.id,
                    "title": task.title,
                    "type": "calendar",
                    "status": "marked as done"
                })

            elif task.schedule_type == "email":
                user = task.user

                payload = {
                    "access_token": user.access_token,
                    "refresh_token": user.refresh_token,
                    "sender_email": task.recipient_email,
                    "subject": task.email_subject,
                    "content": task.email_body,
                    "from_email": user.email,
                }

                resp = requests.post(f"{GMAIL_SERVICE_BASE}/send_reply/", json=payload)

                if resp.status_code == 200:
                    task.done = True
                    task.save(update_fields=["done"])
                    results.append({
                        "task_id": task.id,
                        "title": task.title,
                        "type": "email",
                        "status": "reply sent",
                        "response": resp.json()
                    })
                else:
                    results.append({
                        "task_id": task.id,
                        "title": task.title,
                        "type": "email",
                        "status": "failed",
                        "error": resp.text
                    })

        except Exception as e:
            results.append({
                "task_id": task.id,
                "title": task.title,
                "type": task.schedule_type,
                "status": "error",
                "error": str(e)
            })

    return JsonResponse({"processed_tasks": results})

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import AppUser

@csrf_exempt
def get_fcm_token(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            uid = data.get("uid")
            if not uid:
                return JsonResponse({"error": "UID required"}, status=400)
            
            app_user = AppUser.objects.get(firebase_uid=uid)

            return JsonResponse({"fcm_token": app_user.fcm_token or ""})
        except AppUser.DoesNotExist:
            return JsonResponse({"fcm_token": ""})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import AppUser

@api_view(['POST'])
def logout_user1(request):
    """
    Logs out a user by setting login=False.
    Expects JSON payload: { "uid": "<firebase_uid>" }
    """
    uid = request.data.get('uid')

    if not uid:
        return Response({"error": "UID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = AppUser.objects.get(firebase_uid=uid)
        user.login = False
        user.save()
        return Response({"success": True, "message": "User logged out"}, status=status.HTTP_200_OK)
    except AppUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# views.py in current project
import requests
from django.http import JsonResponse
from .models import AppUser

SUPPORT_URL_mark = "https://mysupportgoogledjango.vercel.app/mark_as_read/"


@csrf_exempt
def mark_as_read(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

 
    data= json.loads(request.body.decode("utf-8"))
    email_id = data.get("email_id")
    uid = data.get("uid")

    if not email_id or not uid:
        return JsonResponse({"error": "Missing email_id or uid"}, status=400)

    try:
        user = AppUser.objects.get(firebase_uid=uid)
    except AppUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Prepare user data for support project
    user_payload = {
        "access_token": user.access_token,
        "refresh_token": user.refresh_token,
        "google_id": user.google_id,
        "email_id": email_id,
    }

    try:
        resp = requests.post(SUPPORT_URL_mark, json=user_payload, timeout=10)
        return JsonResponse(resp.json(), status=resp.status_code)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from .models import AppUser, IgnoredEmail

@csrf_exempt
def add_ignored_email(request):
    """Add or update ignored email for a user."""
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        uid = data.get("uid")
        email_id = data.get("email_id")

        if not uid or not email_id:
            return JsonResponse({"error": "Missing uid or email_id"}, status=400)

        try:
            user = AppUser.objects.get(firebase_uid=uid)
        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        ignored_email, created = IgnoredEmail.objects.get_or_create(user=user, ignored_email=email_id)
        if not created:
            ignored_email.count += 1
            ignored_email.save()

        return JsonResponse({
            "message": "Ignored email saved successfully",
            "ignored_email": email_id,
            "count": ignored_email.count
        })

    return JsonResponse({"error": "Invalid request method"}, status=405)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import AppUser, IgnoredEmail
import json

@csrf_exempt
def get_ignored_emails(request):
    """Fetch ignored emails for a given UID (via POST)."""
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        uid = data.get("uid")

        if not uid:
            return JsonResponse({"error": "UID is required"}, status=400)

        try:
            user = AppUser.objects.get(firebase_uid=uid)
        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        ignored_list = IgnoredEmail.objects.filter(user=user).values(
            "ignored_email", "count", "created_at"
        )

        return JsonResponse({"ignored_emails": list(ignored_list)}, safe=False)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def delete_ignored_email(request):
    """Delete a specific ignored email."""
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        uid = data.get("uid")
        ignored_email = data.get("ignored_email")

        if not uid or not ignored_email:
            return JsonResponse({"error": "UID and ignored_email are required"}, status=400)

        try:
            user = AppUser.objects.get(firebase_uid=uid)
        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        deleted, _ = IgnoredEmail.objects.filter(user=user, ignored_email=ignored_email).delete()

        if deleted:
            return JsonResponse({"message": "Ignored email deleted successfully"})
        else:
            return JsonResponse({"error": "Ignored email not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)


import requests
from django.http import JsonResponse

def call_sf(request):
    """
    Calls the Render `/sf/` endpoint and returns its response.
    """
    url = "https://scheduleyourjob.onrender.com/sf/"
    
    try:
        # Make GET request to Render endpoint
        response = requests.get(url, timeout=120)  # 2-minute timeout
        
        # If Render returns JSON
        try:
            data = response.json()
        except ValueError:
            # If it's not JSON, return plain text
            data = {"message": response.text}

        return JsonResponse({
            "status_code": response.status_code,
            "data": data
        })

    except requests.exceptions.RequestException as e:
        # Catch network or timeout errors
        return JsonResponse({
            "status_code": 500,
            "error": str(e)
        })

# views.py

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import EmailClassification

@csrf_exempt
def check_email_classification(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            uid = data.get("uid")
            email_id = data.get("email_id")
            try:
                obj = EmailClassification.objects.get(uid=uid, email_id=email_id)
                return JsonResponse({
                    "exists": True,
                    "classification": obj.classification,
                    "summary": obj.summary
                })
            except EmailClassification.DoesNotExist:
                return JsonResponse({"exists": False})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST required"}, status=405)


@csrf_exempt
def save_email_classification(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            uid = data.get("uid")
            email_id = data.get("email_id")
            classification = data.get("classification")
            summary = data.get("summary")

            obj, created = EmailClassification.objects.update_or_create(
                uid=uid, email_id=email_id,
                defaults={"classification": classification, "summary": summary}
            )
            return JsonResponse({"status": "saved", "created": created})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST required"}, status=405)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from .models import AppUser, IgnoredEmail, ScheduledTask, Todo
import requests


@api_view(['POST'])
def gmail_stats_view(request):
    uid = request.data.get("uid")
    if not uid:
        return Response({"error": "uid required"}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Validate user
    try:
        user = AppUser.objects.get(firebase_uid=uid)
    except AppUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # 2. Prepare payload for support API
    payload = {
        "access_token": user.access_token,
        "refresh_token": user.refresh_token
    }

    SUPPORT_API_URL = "https://mysupportgoogledjango.vercel.app/gmail_stats/"
    try:
        response = requests.post(SUPPORT_API_URL, json=payload, timeout=30)
        if response.status_code != 200:
            return Response(
                {"error": "Support API error", "details": response.text},
                status=status.HTTP_502_BAD_GATEWAY
            )

        gmail_data = response.json()

        # 3. Add ignored email stats
        ignored_count = IgnoredEmail.objects.filter(user=user).count()

        # 4. Add scheduled task stats
        total_tasks = ScheduledTask.objects.filter(user=user).count()
        completed_tasks = ScheduledTask.objects.filter(user=user, done=True).count()
        pending_tasks = ScheduledTask.objects.filter(user=user, done=False).count()

        # 5. Add todo stats
        total_todos = Todo.objects.filter(user_uid=uid).count()
        done_todos = Todo.objects.filter(user_uid=uid, done=True).count()
        undone_todos = Todo.objects.filter(user_uid=uid, done=False).count()

        # 6. Merge everything
        final_response = {
            **gmail_data,
            "ignored_emails": ignored_count,
            "scheduled_tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "pending": pending_tasks,
            },
            "todos": {
                "total": total_todos,
                "done": done_todos,
                "undone": undone_todos,
            },
        }

        return Response(final_response)

    except Exception as e:
        return Response(
            {"error": "Failed to call support API", "details": str(e)},
            status=status.HTTP_502_BAD_GATEWAY
        )

import json, requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import date
from .models import EmailSummary
 
# Replace with actual support project URL

@csrf_exempt
def get_today_summaries(request):
    
    SUPPORT_API = "https://mysupportgoogledjango.vercel.app/summarize_email/" 
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            emails = payload.get("emails", [])

            result = []

            for email in emails:
                email_id = email.get("id")
                sender = email.get("from", "")
                subject = email.get("subject", "").strip() or "None"

                body = email.get("body", "")

                # Check if summary exists
                summary_obj = EmailSummary.objects.filter(email_id=email_id).first()
                if summary_obj:
                    summary = summary_obj.summary
                else:
                    # Call support project to generate summary
                    res = requests.post(SUPPORT_API, json={
                        "from": sender,
                        "subject": subject,
                        "body": body
                    })

                    if res.status_code == 200:
                        summary = res.json().get("summary", "No summary")
                    else:
                        summary = "Failed to generate summary"

                    # Save in DB
                    EmailSummary.objects.create(
                        email_id=email_id,
                        sender=sender,
                        subject=subject,
                        body=body,
                        summary=summary
                    )

                # Add to response list
                result.append({
                    "id": email_id,
                    "from": sender,
                    "subject": subject,
                    "body": body,
                    "summary": summary
                })

            return JsonResponse({"emails": result}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import EmailClassification,EmailSummary
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def cleanup_old_classifications(request):
    now = timezone.now()

    # Delete records older than 5 days
    five_days_ago = now - timedelta(days=5)
    deleted_5, _ = EmailClassification.objects.filter(created_at__lt=five_days_ago).delete()

    # Delete records older than 2 days
    two_days_ago = now - timedelta(days=2)
    deleted_2, _ = EmailSummary.objects.filter(created_at__lt=two_days_ago).delete()

    return JsonResponse({
        "success": True,
        "deleted_older_than_5_days": deleted_5,
        "deleted_older_than_2_days": deleted_2
    }, status=200)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import AppUser
import requests, json

SUPPORT_PROJECT_URL = "http://127.0.0.1:8000/get_email_data_name/"  # endpoint in support project


@csrf_exempt
def get_email_data_name(request):
    """
    POST: { "firebase_uid": "<UID>", "email_id": "<GMAIL_MESSAGE_ID>" }
    """
    try:
        data = json.loads(request.body)
        firebase_uid = data.get("firebase_uid")
        email_id = data.get("email_id")

        if not firebase_uid or not email_id:
            return JsonResponse({"error": "Missing firebase_uid or email_id"}, status=400)

        # 🧩 Fetch user from DB
        try:
            user = AppUser.objects.get(firebase_uid=firebase_uid)
        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        # ✅ Prepare payload for support project
        payload = {
            "firebase_uid": user.firebase_uid,
            "email": user.email,
            "access_token": user.access_token,
            "refresh_token": user.refresh_token,
            "email_id": email_id,
        }

        # 🔄 Forward to Support project
        res = requests.post(SUPPORT_PROJECT_URL, json=payload, timeout=60)
        return JsonResponse(res.json(), status=res.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



ANOTHER_REPORT_URL = "https://mysupportgoogledjango.vercel.app/smart_report_users/"
#ANOTHER_REPORT_URL = "http://127.0.0.1:8000/smart_report_users/"

import json
import pytz
from datetime import date, datetime
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import OpenRouterAPIKey, AppUser

#ANOTHER_REPORT_URL = "https://mysupportgoogledjango.vercel.app/smart_report_users/"
MAX_PER_DAY = 50

import random
@csrf_exempt
def smart_report_users(request):
    try:
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)
        today = now.date()
        start_time = time(9, 30)
        end_time = time(22, 0)
        if not (start_time <= now.time() <= end_time):
            return JsonResponse({"status": "outside allowed time window"}, status=200)
        # 🔍 Users not processed today
        users = AppUser.objects.filter(login=True).exclude(last_notified_date=today)
        if not users.exists():
            return JsonResponse({"status": "no pending users"}, status=200)

        # 🔥 Limit per run
        users_to_report = users[:3]

        # --------------------------------------------------
        # 1️⃣ RESET API KEYS IF DATE CHANGED
        # --------------------------------------------------
        api_keys_payload = []
        keys = OpenRouterAPIKey.objects.all()

        for k in keys:
            if k.last_reset != today:
                k.requests_today = 0
                k.last_reset = today
                k.save()

            api_keys_payload.append({
                "key": k.key,
                "requests_today": k.requests_today,
                "max_per_day": MAX_PER_DAY
            })
        random.shuffle(api_keys_payload)

        # --------------------------------------------------
        # 2️⃣ BUILD USER PAYLOAD
        # --------------------------------------------------
        user_data_list = []
        for u in users_to_report:
            user_data_list.append({
                "firebase_uid": u.firebase_uid,
                "email": u.email,
                "access_token": u.access_token,
                "refresh_token": u.refresh_token,
                "date_joined": int(u.date_joined.timestamp()),
                "fcm_token": u.fcm_token
            })

        # --------------------------------------------------
        # 3️⃣ CALL SUPPORT PROJECT
        # --------------------------------------------------
        res = requests.post(
            ANOTHER_REPORT_URL,
            json={
                "users": user_data_list,
                "api_keys": api_keys_payload
            },
            timeout=120
        )

        response_data = res.json()

        # --------------------------------------------------
        # 4️⃣ UPDATE API USAGE FROM SUPPORT RESPONSE
        # --------------------------------------------------
        api_usage = response_data.get("api_usage", {})

        for key_value, used_count in api_usage.items():
            try:
                k = OpenRouterAPIKey.objects.get(key=key_value)
                k.requests_today = used_count
                k.last_reset = today
                k.save(update_fields=["requests_today", "last_reset"])
            except OpenRouterAPIKey.DoesNotExist:
                continue
        
        # --------------------------------------------------
        # 5️⃣ MARK USERS AS PROCESSED
        # --------------------------------------------------
        for u in users_to_report:
            u.last_notified_date = today
            u.save(update_fields=["last_notified_date"])

        return JsonResponse({
            "status": "success",
            "sent_users": len(users_to_report),
            "api_usage_updated": api_usage
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




SUPPORT_REPORT_URL = "https://mysupportgoogledjango.vercel.app/reports/"
#SUPPORT_REPORT_URL = "http://127.0.0.1:8000/reports/"

import json
from datetime import date
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
from .models import OpenRouterAPIKey, AppUser
MAX_PER_DAY = 50
@csrf_exempt
def reports(request):
    """
    1. Find user by uid
    2. Reset API key usage if new day
    3. Send user + API keys to support
    4. Receive updated usage
    5. Update DB
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body.decode())
        uid = body.get("uid")

        if not uid:
            return JsonResponse({"error": "uid required"}, status=400)

        # -----------------------------
        # 1. Get User
        # -----------------------------
        try:
            user = AppUser.objects.get(firebase_uid=uid)
        except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        # -----------------------------
        # 2. Prepare API Keys (reset daily)
        # -----------------------------
        today = date.today()
        api_keys_payload = []

        keys = OpenRouterAPIKey.objects.all()
        for k in keys:
            if k.last_reset != today:
                k.requests_today = 0
                k.last_reset = today
                k.save()

            api_keys_payload.append({
                "key": k.key,
                "requests_today": k.requests_today,
                "max_per_day": MAX_PER_DAY
            })
        random.shuffle(api_keys_payload)

        if not api_keys_payload:
            return JsonResponse({"error": "No API keys available"}, status=500)

        # -----------------------------
        # 3. Send to Support Project
        # -----------------------------
        support_payload = {
            "uid": user.firebase_uid,
            "email": user.email,
            "access_token": user.access_token,
            "refresh_token": user.refresh_token,
            "api_keys": api_keys_payload
        }

        support_resp = requests.post(
            SUPPORT_REPORT_URL,
            json=support_payload,
            timeout=120
        )

        if support_resp.status_code != 200:
            return JsonResponse({
                "error": "Support service failed",
                "details": support_resp.text
            }, status=500)

        support_data = support_resp.json()

        updated_keys = support_data.get("api_keys", [])
        emails = support_data.get("emails", [])

        # -----------------------------
        # 4. Update API Key Usage in DB
        # -----------------------------
        for k in updated_keys:
            key_str = k.get("key")
            usage = k.get("requests_today")

            if key_str is None or usage is None:
                continue

            try:
                obj = OpenRouterAPIKey.objects.get(key=key_str)
                obj.requests_today = usage
                obj.save()
            except OpenRouterAPIKey.DoesNotExist:
                continue

        # -----------------------------
        # 5. Final Response
        # -----------------------------
        return JsonResponse({
            "status": "success",
            "uid": uid,
            "emails": emails,
           
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.shortcuts import render, redirect
from django.http import FileResponse
from django.core.mail import send_mail
from .models import MVPUser
import os

MAX_USERS = 30

# =========================
# SPLASH (UNCHANGED)
# =========================
def splash(request):
    return render(request, "core/splash.html")


# =========================
# REGISTER MVP
# =========================
def register_mvp(request):
    if MVPUser.objects.count() >= MAX_USERS:
        return render(request, "core/full_mvp.html")

    error = None

    if request.method == "POST":
        email = request.POST.get("email")

        if MVPUser.objects.filter(email=email).exists():
            error = "This email is already registered."
        else:
            user = MVPUser.objects.create(
                name=request.POST.get("name"),
                email=email,
                phone=request.POST.get("phone")
            )
            request.session["mvp_user_id"] = user.id
            return redirect("disclaimer_mvp")

    return render(request, "core/register_mvp.html", {"error": error})


# =========================
# DISCLAIMER MVP
# =========================
def disclaimer_mvp(request):
    user_id = request.session.get("mvp_user_id")
    if not user_id:
        return redirect("register_mvp")

    user = MVPUser.objects.get(id=user_id)

    if user.accepted_disclaimer:
        return redirect("thankyou_mvp")

    if request.method == "POST":
        user.accepted_disclaimer = True
        user.save()
        return redirect("download_mvp")

    return render(request, "core/disclaimer_mvp.html")


# =========================
# DOWNLOAD MVP
# =========================
def download_mvp(request):
    user_id = request.session.get("mvp_user_id")
    if not user_id:
        return redirect("register_mvp")

    user = MVPUser.objects.get(id=user_id)

    if user.downloaded:
        return render(request, "core/download_mvp.html", {
            "already_downloaded": True
        })

    if request.method == "POST":
        user.downloaded = True
        user.save()

        apk_path = os.path.join(
            "static",
            "core",
            "ForgotYourEmail.apk"
        )

        return FileResponse(
            open(apk_path, "rb"),
            as_attachment=True,
            filename="ForgotYourEmail.apk",
            content_type="application/vnd.android.package-archive"
        )

    return render(request, "core/download_mvp.html", {
        "already_downloaded": False
    })


# =========================
# THANK YOU MVP
# =========================
def thankyou_mvp(request):
    return render(request, "core/thankyou_mvp.html")


# =========================
# ISSUE MVP
# =========================
def issue_mvp(request):
    if request.method == "POST":
        user_email = request.POST.get("email")
        issue_text = request.POST.get("issue")

        send_mail(
            subject=f"Issue on Forgot Your Email by {user_email}",
            message=issue_text,
            from_email=user_email,
            recipient_list=["srinu19773@gmail.com"],
        )

        return render(request, "core/issue_sent_mvp.html")

    return render(request, "core/issue_mvp.html")
