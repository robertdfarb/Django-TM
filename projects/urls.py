from django.conf.urls import url

from . import views

app_name = 'projects'

urlpatterns = [
    url(r"^$", views.MainTasks.as_view(), name="all"),
    url(r'^ajax_tasks/', views.ajax_tasks, name="ajax_tasks"),
    url(r"^add/", views.AddTask.as_view(), name="addtask"),
    url(r"^edit/(?P<pk>\d+)/$", views.EditTask.as_view(), name="edittask"),
    url(r"^assign/(?P<pk>\d+)/$", views.assigntask, name="assigntask"),
    #url(r"^time/(?P<task_id>\d+)/$", views.TimeTask.as_view(), name="timetask"),
    url(r"^time/(?P<task_id>\d+)/$", views.ajax_timelog, name="timetask"),
]
