from django.conf import settings
from django.db.models import Q, Sum, Count, FilteredRelation, Case, When
from django.urls import reverse
from django.db import models
from datetime import datetime, date, time
import calendar
from django.utils.text import slugify
from django.core.validators import MinValueValidator
import django.contrib.auth
from decimal import Decimal
import numpy as np
from tm.utils import deprecated
from .managers import TaskModelManager, TimeLogModelManager, TaskAssignmentQuerySet
from django.db.models.signals import pre_save, post_save
# from accounts.models import User
from django.contrib.auth import get_user_model
import os
#from django.contrib.auth.models import User

User = django.contrib.auth.get_user_model()


######################### MASTER DATA ###########################################

class MasterClient(models.Model):
    name                            = models.CharField(max_length=50, unique=True)
    contact                         = models.CharField(max_length=50, blank=True)
    phone                           = models.CharField(max_length=50, blank=True)
    owner                           = models.ForeignKey(User, on_delete=models.PROTECT,related_name='ownerscalendar')
    created_by                      = models.ForeignKey(User, on_delete=models.PROTECT,related_name='creatorscalendar')
    created_date                    = models.DateField(auto_now_add=True, blank=True)
    last_modified_by                = models.ForeignKey(User, on_delete=models.PROTECT,related_name='modifierscalendar')
    last_modified_date              = models.DateField(auto_now_add=True, blank=True)
    last_contact_date               = models.DateField(null=True, blank=True)
    required_contact_days           = models.IntegerField()
    active                          = models.BooleanField(default=True)
    billable                        = models.BooleanField(default=True)
    slug                            = models.SlugField(max_length=40)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

class MasterTaskType(models.Model):
    type                           = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = 'MasterTaskType'
        verbose_name_plural ='MasterTaskTypes'


class MasterTaskCategory(models.Model):
    category                         = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name = 'MasterTaskCategory'
        verbose_name_plural ='MasterTaskCategory'

class MasterTaskStatus(models.Model):
    status                      = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = 'MasterTaskType'
        verbose_name_plural ='MasterTaskTypes'

#Posssible future implementation
class MasterBillingCalendar(models.Model):
    user                         = models.ForeignKey(User, on_delete=models.PROTECT,related_name='billingcalendar')
    calendar_month               = models.CharField(max_length=6,null=False, blank=False, unique=True)
    closed_date                  = models.DateField(null=True)
    closed_period                = models.BooleanField(default=False)
    start_date                   = models.DateField(null=True)
    end_date                     = models.DateField(null=True)
        #create standard calendar
    def __str__(self):
        return calendar_month

#######################################  PROJECT MODELS ########################################################

# Represents and Engagement or Case Number
class Project(models.Model):
    name                            = models.CharField(
                                            max_length=100,
                                            unique=True,
                                            error_messages={
                                                "unique": "An engagement with this name already exists, the engagement name must  be unique"
                                                })
    client                          = models.ForeignKey(MasterClient,on_delete=models.PROTECT, related_name='clientprojects')
    owner                           = models.ForeignKey(User, on_delete=models.PROTECT,related_name='ownersprojects') # Specific Owner for Project
    created_by                      = models.ForeignKey(User, on_delete=models.PROTECT,related_name='creatorsprojects')
    created_date                    = models.DateField(auto_now_add=True, blank=True)
    billable                        = models.BooleanField(default=True)
    last_modified_by                = models.ForeignKey(User, on_delete=models.PROTECT,related_name='modifiersprojects')
    last_modified_date              = models.DateField(auto_now_add=True, blank=True)
    project_start_date              = models.DateField(auto_now_add=True, blank=True)
    #assigned_users                  = models.ManyToManyField(User,related_name='usersassigned',through='projectuser') ##is this a real field?
    due_date                        = models.DateTimeField(blank=True,null=True)
    budgeted_hrs                    = models.DecimalField(max_digits=8, decimal_places=2,validators=[MinValueValidator(Decimal('0.00'))])
    last_contact_date               = models.DateField(null=True, blank=True)
    required_contact_days           = models.IntegerField()
    comments                        = models.TextField(blank=True, default='')
    completed_date                  = models.DateField(blank=True,null=True)
    active                          = models.BooleanField(default=True)
    slug                            = models.SlugField(max_length=40)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def project_model_pre_save_reciever(sender,instance,*args,**kwargs):
        print("before save")
        if not instance.slug and instance.name:
            instance.slug = slugify(instance.name)
            pre_save.connect(project_model_pre_save_reciever,sender=Project)

#Possible add on feature to allow only control user access to specific cases.
class ProjectUser(models.Model):

    project                         = models.ForeignKey(Project, on_delete=models.PROTECT, default='Unassigned',related_name='projects')
    user                            = models.ForeignKey(User,on_delete=models.PROTECT,related_name='projectusers')

    def __str__(self):
        return "Project: {project}".format(project=self.project.name)

    class Meta:
        verbose_name = 'ProjectUser'
        verbose_name_plural ='ProjectUserAssigned'
        unique_together = ("project", "user")

##Possible consideration of ability to subtask a task.  Recursive approach.
class Task(models.Model):

    SOURCES = (
        ('U', 'UserCreated'),
        ('A', 'Assigned'),
    )

    subject                         = models.CharField(max_length=40)
    parent                          = models.IntegerField(blank=True, null=True)  # Default this as the top_level_id of the task we are working on, allowing for the ability to recurivesly look at original tasks for a subtask much faster.
    project                         = models.ForeignKey(Project, on_delete=models.PROTECT,related_name='projecttasks')
    source_of_entry                 = models.CharField(max_length=1, choices=SOURCES, blank=True)
    billable                        = models.BooleanField(default=True)
    owner                           = models.ForeignKey(User, on_delete=models.PROTECT,related_name='taskowner',blank=True, null=True)
    created_by                      = models.ForeignKey(User, on_delete=models.PROTECT,related_name='taskcreator')
    created_date                    = models.DateTimeField(auto_now_add=True, blank=True)
    last_modified_by                = models.ForeignKey(User, on_delete=models.PROTECT,related_name='taskmodifier', blank=True, null=True)
    last_modified_date              = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    category                        = models.ForeignKey(MasterTaskCategory, on_delete=models.PROTECT,related_name='tasktype', blank=True, null=True)
    type                            = models.ForeignKey(MasterTaskType, on_delete=models.PROTECT,related_name='tasktype')
    description                     = models.TextField(blank=True, max_length=300, default='')
    due_date                        = models.DateField(blank=True, null=True)
    status                          = models.ForeignKey(MasterTaskStatus, on_delete=models.PROTECT,related_name='taskstatus',blank=True, null=True,)
    budgeted_hrs                    = models.DecimalField(max_digits=8, decimal_places=2,validators=[MinValueValidator(Decimal('0.00'))])
    completed_date                  = models.DateTimeField(blank=True, null=True)
    active                          = models.BooleanField(default=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural ='Tasks'

    objects = TaskModelManager()      #original Default models.Manager()

    unique_together = ('project','subject')

    def save(self, *args, **kwargs):
        if not self.pk:
            print ("This is a new record")
            super(Task,self).save(args, kwargs)
            print ("Now it has a PK of " + str(self.id))
            self.taskassigned.create(user_assigned=self.created_by,user_assigned_by=self.created_by)
            print ("Task has been assigned")
        else:
            print ("Record Edited " + str(self.id))
            super(Task,self).save(args, kwargs)


#History of the task assignment. A task defaults to the user that created it, and it can be reassigned as many times as needed.  A person in the chain of assignment will be able to see all
#tasks that they assigned.

class TaskAssignment(models.Model):

    task                            = models.ForeignKey(Task,on_delete=models.PROTECT,related_name='taskassigned')
    task_parent                     = models.IntegerField(unique=False, blank=True, null=True)
    user_assigned                   = models.ForeignKey(User,on_delete=models.PROTECT,related_name='assigneduser')
    user_assigned_by                = models.ForeignKey(User,on_delete=models.PROTECT,related_name='assignedbyuser')
    active                          = models.BooleanField(default=True)
    priority                        = models.IntegerField(unique=False, blank=True, null=True)
    assigned_date                   = models.DateField(blank=True, null=True)
    due_date                        = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.task.id)

    class Meta:
        verbose_name = 'TaskAssignment'
        verbose_name_plural ='TaskAssignments'
        unique_together = ('task', 'user_assigned','active')
        ordering = ['priority']

    #objects = TaskAssignmentQuerySet.as_manager()

#Possible Future Implementation
class DocumentManagement(models.Model):

    def upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/client_slug/project_slug_/<filename>
        path = os.path.join(instance.task.project.client.slug,instance.task.project.slug,filename)
        print (path)
        return str(path)

    task                         = models.ForeignKey(Task,on_delete=models.PROTECT,related_name='documenttask')
    owner                        = models.ForeignKey(User,on_delete=models.PROTECT,related_name='documentowner')
    file                         = models.FileField(upload_to=upload_path, blank=True)  ##Upload to specific client path | ProjectPath
    created_by                   = models.ForeignKey(User, on_delete=models.PROTECT, related_name='documentcreator')
    approval_required            = models.BooleanField(default=True)
    reviewer_assigned            = models.ForeignKey(User, on_delete=models.PROTECT, related_name='documentreviewer')
    created_date                 = models.DateTimeField(auto_now_add=True, blank=True)
    last_modified_by             = models.ForeignKey(User, on_delete=models.PROTECT,related_name='documentmodifier')
    last_modified_date           = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural ='Documents'

    #create a new review task for document review
    def create_review_task():
        pass

# This will just be a single table of task history
class TimeLog(models.Model):

    TIME_TYPES = (
        ('B', 'Billable'),
        ('A', 'Actual'),
    )

    SOURCES = (
        ('T', 'Timer'),
        ('M', 'Manual'),
        ('A', 'Task Assignment'),
    )

    task                         = models.ForeignKey(Task, on_delete=models.PROTECT,related_name='timeloggedtask')
    source_of_entry              = models.CharField(max_length=1, choices=SOURCES, blank=True)
    loggeduser                   = models.ForeignKey(User, on_delete=models.PROTECT,related_name='timeloggeduser')
    created_by                   = models.ForeignKey(User, on_delete=models.PROTECT, related_name='timeloggedcreator')
    created_date                 = models.DateTimeField(auto_now_add=True, blank=True)
    last_modified_by             = models.ForeignKey(User, on_delete=models.PROTECT, related_name='timelogmodifier')
    last_modified_date           = models.DateTimeField(null=True)
    date_time_started            = models.DateTimeField(auto_now_add=True, blank=True)
    date_time_ended              = models.DateTimeField(null=True)
    comments                     = models.TextField(blank=True, max_length=300, default='') #Comments related to the logging of the task
    #Ability to log time as billed seperately as billable amounts may be entered later and are really itemized by task
    #type                         = models.CharField(max_length=1, choices=TIME_TYPES, blank=True)
    actualhrs                    = models.DecimalField(max_digits=8, decimal_places=2)
    billablehrs                  = models.DecimalField(max_digits=8, decimal_places=2)
    hrs_verified                 = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'TimeLog'
        verbose_name_plural ='HoursLogged'

    def __str__(self):
        return "taskid: {id} time: {ts}".format(id=str(self.task_id),ts=str(self.date_time_started))


#### LogHistory for time spent on site, track time type, breaks etc.
