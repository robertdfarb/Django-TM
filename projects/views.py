from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import(
    LoginRequiredMixin,
    PermissionRequiredMixin
)

from django.urls import reverse, reverse_lazy
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from accounts.models import MyUser
from django.http import JsonResponse
from . import forms
import json
from .models import (
        Project,
        ProjectUser,
        Task,
        MasterClient,
        TimeLog,
        TaskAssignment
)


class MainTasks(LoginRequiredMixin, generic.TemplateView):
    template_name = 'projects/tasks.html'


@login_required
def ajax_tasks(request):
    if request.is_ajax():
        print ("Ajax call made")
        currentuser = request.user
        qs = Task.objects.get_assigned(currentuser.id).tasks_with_totalhrs(currentuser.id)
        return JsonResponse(list(qs),safe=False)
    else:
        return HttpReponse("Bad Response")


class AddTask(LoginRequiredMixin, generic.CreateView):
    template_name = 'projects/_addtaskform.html'
    form_class = forms.TaskForm
    success_url = reverse_lazy('projects:all')

    #sets initial values for a form
    def get_initial(self):
        initial = super(AddTask, self).get_initial()
        initial['created_by'] =self.request.user.id
        return initial


class EditTask(LoginRequiredMixin, generic.UpdateView):
    template_name = 'projects/_edittaskform.html'
    form_class = forms.TaskForm
    model = Task
    success_url = reverse_lazy('projects:all')


class AssignTask(LoginRequiredMixin, generic.DetailView):
    template_name = 'projects/_assigntaskform.html'
    model = TaskAssignment
    form_class = forms.AssignTaskForm
    success_url = reverse_lazy('projects:all')


@login_required
def assigntask(request,*args, **kwargs):
    if request.method == 'GET':
        print ('GET Request')
        pk = kwargs.get('pk')
        print (kwargs.get('pk'))
        assigned = TaskAssignment.objects.filter(task__id=pk).first()
        print (assigned.user_assigned)
        print (dir(assigned))
        data = {'user': assigned.user_assigned,
                'due_date': assigned.due_date,
                'form' : forms.AssignTaskForm
               }
        return render(request, template_name='projects/test.html', context=data)
    else:
        return HttpResponse("no response")


@login_required
def ajax_timelog(request,task_id):
    if request.is_ajax():
        print ("Ajax call made to timelog")
        currentuser = request.user
        task_number = task_id
        qs = TimeLog.objects.filter(task=task_number)
        return JsonResponse(list(qs),safe=False)
    else:
        return render(request, template_name='projects/_timelog.html')


class TimeTask(LoginRequiredMixin, generic.ListView):
    template_name = 'projects/_timelog.html'
    context_object_name ='loggedtime'

    def get_queryset(self):
        task_number = self.kwargs['task_id']
        qs = TimeLog.objects.filter(task=task_number)
        return qs
