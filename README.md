ForgotYourEmail – Smart Email Assistant (Android + Django)

ForgotYourEmail is an intelligent email-management system that automatically fetches, classifies, and processes Gmail emails using machine learning. It provides actionable notifications, AI-generated auto-replies, scheduling features, and task management — all integrated seamlessly between Android, Django, Gmail API, and Firebase.

🚀 Initial Version

📌 Initial MVP Model Released: 21 December 2025
Link:  https://forgotyouremail.vercel.app/

📱 Features
1. Gmail Email Sync

Sign in using Firebase Authentication (Google Sign-In)

Securely fetch unread Gmail emails using the Gmail API

Sync only emails after the user’s join date

2. Email Classification

Emails are classified into 4 categories:

Auto Reply

Schedule

To-Do

Ignore

Classification is done via: A Django backend that calls the deployed ML API


3. Actionable Push Notifications

Uses Firebase Cloud Messaging (FCM HTTP v1 API) to deliver notifications with buttons:

Auto Reply

Schedule

To-Do

Ignore

Handled by a BroadcastReceiver in Android.

4. Auto Reply Generation

Fetches complete email (sender, subject, body)

Sends details to backend

Django fetches email from Gmail + generates reply via Gemini

User can: Edit subject & content

Regenerate

Send reply directly from this app

5. To-Do Functionality

Each task includes:

Task title (default = email subject)

User-defined content

Status: Pending / Done

Options: Edit, Delete, Mark as Done

6. Scheduling

Allows scheduling events based on email content

Django updates events on Google Calendar

7. Automatic Email Update

After user performs:

Auto Reply

Schedule

To-Do

Ignore

→ Corresponding Gmail email is marked as read.

🏗 Architecture Overview
Android (Frontend)

Kotlin

Firebase Auth

Gmail API

FCM Notifications

Activities:

AutoReplyActivity

ScheduleActivity

TodoListActivity

TestClassifierActivity

Backend (Django)

Stores:

User Firebase UID

Email

Google Access/Refresh Tokens

FCM Token

Join date

Login flag

Handles:

Email sync

Classification

Auto-reply logic

Push notifications

Scheduling

🧪 Tech Stack
Mobile

Kotlin (Android)

Firebase Authentication

FCM HTTP v1 API

Gmail API

TFLite (local testing)

Backend

Django / Django REST Framework

Google OAuth APIs

Python ML API integration

CRON / Background tasks



✔️ Current Status

MVP Released on 21 Dec 2025
Link:  https://forgotyouremail.vercel.app/

Major features implemented (Email sync, classification, actions, AI replies)

Stable for testing and user feedback


Venkateswara Rao Bhimasingi – Developer (Android + Django)
