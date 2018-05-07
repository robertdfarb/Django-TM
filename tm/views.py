from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

# Create your views here.
class HomePage(TemplateView):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("projects:all"))
        return super().get(request, *args, **kwargs)
