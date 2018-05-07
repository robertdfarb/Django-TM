from django import forms
from projects import models

class TaskForm(forms.ModelForm):

    due_date = forms.DateField(widget=forms.SelectDateWidget(empty_label=("Nothing"),),)
    desciption = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = models.Task
        fields = ['project','subject','billable','type','description','due_date','budgeted_hrs','created_by']

        labels = {
            'project': 'Case Name',
            'subject': 'Subject',
            'bilable': 'Billable',
            'type': 'Task Type',
            'description': 'Notes',
            'due_date': 'Date Due',
            'budgeted_hrs':'Budgeted Hours',
            'created_by': 'Created By',
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args,**kwargs)

class AssignTaskForm(forms.ModelForm):

    due_date = forms.DateField(widget=forms.SelectDateWidget(empty_label=("Nothing"),),)

    class Meta:
        model = models.TaskAssignment
        fields = ['user_assigned','due_date']

        labels = {
            'user_assigned': 'Assigned To',
            'due_date': 'Assignment Due Date',
        }

    def __init__(self, *args, **kwargs):
        super(AssignTaskForm, self).__init__(*args,**kwargs)
        #self.fields['description'].widget = forms.TextArea()
