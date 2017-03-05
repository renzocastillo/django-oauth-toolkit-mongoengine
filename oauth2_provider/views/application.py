from django.core.urlresolvers import reverse_lazy
# from django.forms.models import modelform_factory
# from django.views.generic import CreateView, DetailView, DeleteView, ListView, UpdateView
from django_mongoengine.views import CreateView, DetailView, DeleteView, ListView, UpdateView
from django_mongoengine.forms import DocumentForm
from django_mongoengine.forms.documents import documentform_factory

from django.conf import settings
from django.utils.module_loading import import_string

from braces.views import LoginRequiredMixin, SuperuserRequiredMixin
from ..models import get_application_model


class ApplicationOwnerIsUserMixin(LoginRequiredMixin, SuperuserRequiredMixin):
    """
    This mixin is used to provide an Application queryset filtered by the current request.user.
    """
    fields = '__all__'

    def get_queryset(self):
        return get_application_model().objects()


class ApplicationRegistration(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    """
    View used to register a new Application for the request.user
    """
    template_name = "oauth2_provider/application_registration_form.html"

    def get_form_class(self):
        """
        Returns the form class for the application model
        """
        # return ApplicationForm
        return documentform_factory(
            get_application_model(),
            fields=('name', 'client_id', 'client_secret', 'client_type',
                    'authorization_grant_type', 'redirect_uris')
        )

    def form_valid(self, form):
        auth_user_model = settings.MONGOENGINE_USER_DOCUMENT
        User = import_string(auth_user_model)
        form.instance.user = User.objects.get(id=self.request.user.id)
        return super(ApplicationRegistration, self).form_valid(form)


class ApplicationDetail(ApplicationOwnerIsUserMixin, DetailView):
    """
    Detail view for an application instance owned by the request.user
    """
    context_object_name = 'application'
    template_name = "oauth2_provider/application_detail.html"


class ApplicationList(ApplicationOwnerIsUserMixin, ListView):
    """
    List view for all the applications owned by the request.user
    """
    context_object_name = 'applications'
    template_name = "oauth2_provider/application_list.html"


class ApplicationDelete(ApplicationOwnerIsUserMixin, DeleteView):
    """
    View used to delete an application owned by the request.user
    """
    context_object_name = 'application'
    success_url = reverse_lazy('oauth2_provider:list')
    template_name = "oauth2_provider/application_confirm_delete.html"


class ApplicationUpdate(ApplicationOwnerIsUserMixin, UpdateView):
    """
    View used to update an application owned by the request.user
    """
    fields = ('client_id', 'client_secret', 'client_type', 
              'authorization_grant_type', 'name', 'redirect_uris')
    context_object_name = 'application'
    template_name = "oauth2_provider/application_form.html"
