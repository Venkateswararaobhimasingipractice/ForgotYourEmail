from django.urls import path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.urls import re_path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('register/', views.custom_register, name='register'),
    path('home/', views.home, name='home'),
    path('logout/', views.custom_logout, name='logout'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path("api/users/login/", views.login_user,name="login_user"),
    path("api/users/register/", views.register_user, name="register_user"),
    path('api/users/profile/', views.save_profile,name="sprofile"),
    path('api/users/get_profile/', views.get_profile,name="gprofile"),
    
    path('api/users/check_type/', views.check_type, name="check_type"),
    path('check_user_type/', views.check_type, name="check_type1"),


    path('api/users/updatetype/', views.updatetype, name="updateusertype"),
    path('api/users/link_google/', views.link_google_account, name='link_google'),
    path("api/users/get_access_token/", views.get_valid_access_token, name="get_valid_access_token"),
    path('homepage/', views.home, name='homepage'),

    path('refresh_all_tokens/', views.refresh_all_access_tokens,name='refresh_all_tokens'),
    path("api/get-access-token/", views.get_access_token,name="get_access_token"),

    path("api/get-join-date/", views.get_join_date,name="get_join_date"),  

    path('api/user_action/', views.user_action,name='user_action'),
    path('api/add_todo/', views.add_todo),
    path('api/mark_todo_done/', views.mark_todo_done),
    path('api/delete_todo/', views.delete_todo),
    path('api/update_todo/', views.update_todo),
    path('api/get_todos/', views.get_todos),
   
   
    path('api/schedules/', views.get_schedules, name='get_schedules'),
    path('api/add_schedule/', views.add_schedule_api,name='add_scheduleapi'),
    path('api/update_schedule/', views.update_schedule_api, name='update_scheduleapi'),
    path('api/delete_schedule/', views.delete_schedule_api, name='delete_scheduleapi'),
    path('mark_due_tasks_done/', views.mark_due_tasks_done, name='mark_due_tasks_done'),
    path('api/logout/',views.logout_user1,name='logout_user1'),
    path('get_today_summaries/', views.get_today_summaries, name='get_today_summaries'),
    
   
    

    
    



    #SPLIT
    path('sync_and_notify_users/',views.sync_and_notify_users,name='sync_and_notify_users'),
    path('sync_and_notify_users5/',views.sync_and_notify_users5,name='sync_and_notify_users5'),
    path('generate_reply_from_email/',views.generate_reply_from_email,name='generate_reply_from_email'),
    path('send_auto_reply/', views.send_auto_reply, name='send_auto_reply'),
    path('add_schedule/', views.add_schedule, name='add_schedule'),
    path('process_due_emails/', views.process_due_emails, name='process_due_emails'),
    path('update_schedule/',views.update_schedule,name='update_schedule'),
    path('delete_schedule/',views.delete_schedule,name='delete_schedule'),
    path("get_pending_schedules/", views.get_pending_schedules, name="get_pending_schedules"),
    path("get_completed_schedules/", views.get_completed_schedules, name="get_completed_schedules"),

    path("create_task/", views.create_task,name="create_task"),
    path("get_tasks/", views.get_tasks,name="get_tasks"),
    path("update_task/", views.update_task,name="update_task"),
    path("delete_task/", views.delete_task,name="delete_task"),

    path('handle_auth_code/', views.handle_auth_code, name='handle_auth_code'),
    path('process_due_tasks/',views.process_due_tasks,name='process_due_tasks'),
    path('api/get_fcm_token/',views.get_fcm_token,name='get_fcm_token'),

    path('mark_as_read/',views.mark_as_read,name='mark_as_read'),
    path('ignore_add/', views.add_ignored_email, name='add_ignored_email'),
    path('ignore_list/', views.get_ignored_emails, name='get_ignored_emails'),
    path('ignore_delete/', views.delete_ignored_email, name='delete_ignored_email'),

    path('call_sf/', views.call_sf, name='call_sf'),
     path("email_classifications/check/", views.check_email_classification, name="check_email_classification"),#not used 
    path("email_classifications/save/", views.save_email_classification, name="save_email_classification"),#not used
    path('store_classification/',views.store_classification,name='store_classification'),
    path('gmail_stats/',views.gmail_stats_view,name='gmail_stats_view'),
    path('cleanup_old_classifications/',views.cleanup_old_classifications,name='cleanup_old_classifications'),
    path('get_email_data_name/', views.get_email_data_name, name='get_email_data_name'),
    path('smart_report_users/', views.smart_report_users, name='smart_report_users'),
    path('reports/', views.reports, name='reports'),
    path('get_all_schedules/',views.get_all_schedules,name='get_all_schedules'),
    path('get_all_tasks/',views.get_all_tasks,name='get_all_tasks'),


    #MVP
     path("", views.splash, name="splash"),

    path("register_mvp/", views.register_mvp, name="register_mvp"),
    path("disclaimer_mvp/", views.disclaimer_mvp, name="disclaimer_mvp"),
    path("download_mvp/", views.download_mvp, name="download_mvp"),
    path("issue_mvp/", views.issue_mvp, name="issue_mvp"),
    path("thankyou_mvp/", views.thankyou_mvp, name="thankyou_mvp"),
]






