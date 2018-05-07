    @deprecated
    def get_logged_tasks(self, currentuser):
        currentdatetime = datetime.now()
        #currentusertasks = qs.filter(task__loggeduser_id=currentuser)
        logged_tasks = TimeLog.objects.filter(loggeduser_id=currentuser) \
            .filter(date_time_ended__day=currentdatetime.day).values('type').annotate(loggedhours = Sum('hrs'), loggedcnt=Count('hrs'))

        print(logged_tasks.query) ##useful attribute to show sql query that will be run
        return logged_tasks

    @deprecated
    def all_tasks_withhrs_ex1(self, currentuser='1'):
        logged_tasks = Task.objects.filter(timelogged__loggeduser_id=currentuser).values() \
                                    .annotate(actualhrs = Sum(Case(When(timelogged__type='A', then='timelogged__hrs'),default=0), output_field=models.DecimalField(max_digits=4, decimal_places=2)), \
                                     billablehrs = Sum(Case(When(timelogged__type='B', then='timelogged__hrs'),default=0), output_field=models.DecimalField(max_digits=4, decimal_places=2)))
        return logged_tasks


    @deprecated
    def hrs_complete(self,begin_range,user='1',type='A',end_range=datetime.now()):
        qs = self.objects.filter(loggeduser=user).filter(type=type).filter(date_time_ended__gte=begin_range).filter(date_time_ended__lte=end_range).values('task_id').annotate(Sum('hrs'))
        return qs

    @deprecated
    def all_tasks_withhrs_ex2(self, currentuser='1'):
        logged_tasks = Task.objects.filter(timelogged__loggeduser_id=currentuser).values().annotate(actualhrs = Sum('timelogged__hrs', filter=Q(timelogged__type='A')))
        return logged_tasks

    @deprecated
    def all_tasks_withhrs_ex3(self, currentuser='1'):
        logged_tasks = Task.objects.filter(timelogged__loggeduser_id=currentuser).values().annotate(actualhrs = Sum('timelogged__hrs', filter=Q(timelogged__type='A')), \
        billedhrs = Sum('timelogged__hrs', filter=Q(timelogged__type='B')))
        return logged_tasks


        #print (dayhours)
        #actual_hrsday = day_hours.filter(time_type='A')[0].get('loggedhours',0.00))  # I believe this would run two seperate queries.
        #billble_hrsday = day_hours.filter(time_type='A')[0].get('loggedhours',0.00))
        #month_hours = HoursLogged.objects.filter(loggeduser_id=currentuser) \
        #    .filter(date_time_ended__month=currentdatetime.month).values('time_type').annotate(loggedhours =Sum('hrs'), loggedcnt=Count('hrs'))


        #qs2 = qs.fetch_reverse_relations('task')
        ##qs2 = HoursLogged.objects.filter(task_id__in=currentusertasks)  Subquery approach will be slow
        #print (dayhours.filter(time_type='B'))

        #print (dayhours['time_type'])

        #qs2 = qs.selected_related('task') #filter(task__loggeduser_id=currentuser)

        # Consider adding current user to the queryset manager
        #qs_currentuser = qs.filter(hourslogged__loggeduser_id=currentuser)

        #qs_dayhrs = qs_currentuser.filter(hourslogged__date_time_ended__day=currentdatetime.day) \
        #    .values('hourslogged__time_type').annotate(loggedhours =Sum('hourslogged__hrs'), loggedcnt=Count('hourslogged__hrs'))
        #qs_monthlyhrs = qs_currentuser.filter(hourslogged__date_time_ended__month=currentdatetime.month) \
        #    .values('hourslogged__time_type').annotate(loggedhours =Sum('hourslogged__hrs'), loggedcnt=Count('hourslogged__hrs'))


    #    if period == 'day':
    #        billed_hrsqs = qs_currentuser.filter(hourslogged__time_type=timetype,hourslogged__date_time_ended__day=currentdatetime.day)
    #        billed_hrs = billed_hrsqs.aggregate(tot_hrs=models.Sum('hourslogged__hrs')).get('tot_hrs',0.00)

    #        if billed_hrs is None:
    #            billed_hrs = 0

        #elif period == 'month':
    #        billed_hrsqs = qs_currentuser.filter(hourslogged__time_type=timetype,hourslogged__date_time_ended__month=currentdatetime.month)
    #        billed_hrs = billed_hrsqs.aggregate(tot_hrs=models.Sum('hourslogged__hrs')).get('tot_hrs',0.00)

    #        if billed_hrs is None:
    #            billed_hrs = 0
    3    #else billed_hrs = 0
    #    return billed_hrs

            #allow for filtering by periods

            #get user task,get active tasks,BilledToday,BilledThisWeek,BilledThisMonth,EstimatedThisMonth
            #Consider using a reverse manager to make this more robust

    '''
        def populate_data(self, user=User.objects.get(id='1')):
            #get the last date
            try:
                last_date = self.objects.all().order_by('end_date')[0].end_date
                print ("Located Previously Populated Dates")
            except:
                last_date = datetime.now()
                print (last_date)

            current_date = (last_date.year, last_date.month, 1)
            #current_date = date(2060, 1, 1)
            year = current_date.year
            month = current_date.month

            for x in range (0, (12 * 10)):

                if month == 12:
                    month = 1
                    year +=1
                else:
                    month +=1

                calendar_month = str(year) + str(month).zfill(2)
                start_date = current_date = date(year, month, 1)
                end_date = calendar.monthrange(year, month)[1]
                current_date = date(year,month, 1)
                end_date = date(year, month, calendar.monthrange(year, month)[1])
                self.objects.create(user=user,calendar_month=calendar_month,closed_date='', closed_period=False, start_date=current_date,end_date=end_date)

            print ('Populated Data for ' + str(x)  + 'Rows')

            #Test Creation:  MonthlyBudgeting.objects.create(user=User.objects.get(id=1),calendar_month='201604',start_date='2016-04-01',end_date='2016-04-30')

        @property
        def workdays_in_month(self):
            days = np.busday_count(self.start_date,self.end_date)
            return days

        @property
        def days_in_month(self):
            days = self.end_date - self.start_date
            return days.days

    '''

    class AjaxClassBasedViewEx(LoginRequiredMixin, generic.ListView):
        model = Task
        template_name = 'projects/tasks.html'
        context_object_name = 'tasks'

        def get_queryset(self, *args, **kwargs):
            currentuser = self.request.user
            loggedtasks = Task.objects.tasks_with_totalhrs(user=currentuser.id)
            print ('Logged in User: ' + currentuser.email)
            return loggedtasks

        def all_hrs(self):
            qs = TimeLog.objects.timelog_day()
            return qs

        def render_to_response(self, context, **response_kwargs):
            if self.request.is_ajax():
                print ("Ajax call made")
                currentuser = self.request.user
                qs = self.get_queryset()
                return JsonResponse(list(qs),safe=False, **response_kwargs)
            else:
                print ("Regular Render To Response Method Called")
                return super(AllTasks,self).render_to_response(context, **response_kwargs)
