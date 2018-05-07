from django.contrib import admin
from datetime import datetime, date, time
from . import models
# Register your models here.



class MasterClientAdmin(admin.ModelAdmin):

    readonly_fields = ['created_by', 'created_date', 'last_modified_by', 'last_modified_date']
    prepopulated_fields = {'slug': ('name',)}

    class Meta:
        fields = ['__all__']

    def save_model(self, request, instance, form, change):
        user = request.user
        instance = form.save(commit=False)

        if change and instance.created_by:
            print ("modified record")
            instance.last_modified_by = user
            instance.last_modified_date = datetime.now()

        if not change or not instance.created_by:
            print ("created record")
            instance.created_by = user
            instance.last_created_date = datetime.now()
            instance.last_modified_by = user
            instance.last_modified_date = datetime.now()

        instance.save()
        form.save_m2m()
        return instance

class ProjectAdmin(admin.ModelAdmin):

    readonly_fields = ['created_by', 'created_date', 'last_modified_by', 'last_modified_date']
    prepopulated_fields = {'slug': ('name',)}

    class Meta:
        fields = ['__all__']

    def save_model(self, request, instance, form, change):
        user = request.user
        instance = form.save(commit=False)

        if change and instance.created_by:
            print ("modified record")
            instance.last_modified_by = user
            instance.last_modified_date = datetime.now()

        if not change or not instance.created_by:
            print ("created record")
            instance.created_by = user
            instance.last_created_date = datetime.now()
            instance.last_modified_by = user
            instance.last_modified_date = datetime.now()

        instance.save()
        form.save_m2m()
        return instance

admin.site.register(models.MasterClient, MasterClientAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.MasterTaskStatus)
admin.site.register(models.ProjectUser)
admin.site.register(models.MasterTaskType)
admin.site.register(models.Task)
admin.site.register(models.MasterTaskCategory)
admin.site.register(models.TaskAssignment)
admin.site.register(models.TimeLog)
admin.site.register(models.MasterBillingCalendar)
admin.site.register(models.DocumentManagement)
