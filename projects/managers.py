from django.conf import settings
from django.db.models.functions import Coalesce
from django.db.models import Q, Sum, Count, FilteredRelation, Case, When
from django.urls import reverse
from django.db import models
from tm.utils import week_date_range
from datetime import date, datetime, time
import datetime as datetime2
import calendar
from django.utils.text import slugify
from tm.utils import deprecated
# from accounts.models import User
#from django.contrib.auth import get_user_model

#User = get_user_model()


class TaskModelQuerySet(models.QuerySet):

    def tasks_with_totalhrs(self, user):
        actual_hrs = Coalesce(Sum('timeloggedtask__actualhrs'),0)
        billed_hrs = Coalesce(Sum('timeloggedtask__billablehrs'),0)
        return self.values('id','subject','type__type','project__name','project__client__name','project__last_contact_date','budgeted_hrs', 'description','due_date').annotate(actual_hrs = actual_hrs).annotate(billed_hrs = billed_hrs)


    def users_task_list(self, user):
        return self.filter(created_by=user).values('id','subject','type__type','project__name','project__client__name','project__last_contact_date','due_date','budgeted_hrs', 'description')

    def get_assigned(self,user):
        return self.get_queryset().filter(taskassigned__user_assigned=user)

    def tasks_specificuser_hrs_logged(self, user):
        actual_hrs_day = Coalesce(Sum('timeloggedtask__actualhrs', filter=Q(timeloggedtask__loggeduser=user)),0)
        billed_hrs_day = Coalesce(Sum('timeloggedtask__billablehrs', filter=Q(timeloggedtask__loggeduser=user)),0)
        return self.values('id','subject','type__type','project__name','project__client__name','project__last_contact_date','budgeted_hrs', 'description').annotate(actualhrs_day = actual_hrs_day).annotate(billed_hrs_day = billed_hrs_day)


class TaskModelManager(models.Manager):

    def get_queryset(self):
        return TaskModelQuerySet(self.model, using=self._db)

    def users_task_list(self, user):
        return self.get_queryset().users_task_list(user)

    def get_assigned(self,user):
        return self.get_queryset().filter(taskassigned__user_assigned=user)

    def tasks_with_totalhrs(self, user):
        return self.get_queryset().tasks_specificuser_hrs_logged(user)

class TimeLogModelManager(models.Manager):

    def get_queryset(self):
        return self.get_queryset().tasks_specificuser_hrs_logged(self)



    def filter_specific_user(self, user):
        return self.get_queryset().filter(loggeduser=user)

    def timelog_day(self, day=datetime2.date.today().day):
        return self.get_queryset().filter(date_time_ended__day=day).annotate(actual_hrs=Sum('actualhrs'))

    def timelog_week(self, day=datetime2.date.today()):
        begin_date_week, end_date_week = utils.week_date_range(day)
        return self.get_queryset().filter(date_time_ended__lte=begin_date_week).filter(date_time_ended__gte=end_date_week)

    def timelog_month(self, month=datetime2.date.today().month):
        return self.get_queryset().filter(date_time_ended__month__lte=month)

    def logged_hrs(self):
        return self.annotate(actualhrs= Sum('actualhrs'),billablehrs= Sum('billablehrs'))

class TaskAssignmentQuerySet(models.QuerySet):

    def get_query_set():
        return self.objects.all()

    def active(self):
        return self.filter(active=True)

    def only_parent(self):
        return self.filter(task=self.task_parent)

    def assigned(self, user):
        return self.filter(user_assigned=user)

    def get_related_tasks(self):
        return self.select_related('task')

    def get_tasks(self,user):
        return self.filter(active=True).filter(user_assigned=user).select_related('task')
