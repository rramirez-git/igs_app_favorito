from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from igs_app_base.utils.utils import crud_list_toolbar
from igs_app_base.utils.utils import crud_toolbar
from igs_app_base.utils.utils import get_from_request
from igs_app_base.views import GenericCreate
from igs_app_base.views import GenericDelete
from igs_app_base.views import GenericDeleteMany
from igs_app_base.views import GenericList
from igs_app_base.views import GenericRead
from igs_app_base.views import GenericUpdate
from igs_app_base.views import GenericViews

from .forms import MainForm
from .forms import UsrMainForm
from .models import Favorito

views = GenericViews(
    Favorito, "Favorito", "Favoritos",
    "administrar", MainForm, MainForm, MainForm)


class UsrList(GenericList):
    model = Favorito
    titulo = "Mis Favoritos"

    def get_queryset(self):
        return self.request.user.mis_favoritos.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["toolbar"] = crud_list_toolbar(
            self.request.user, self.model, blinder_model="mine_fav")
        context['mine'] = True
        return context


class UsrRead(GenericRead):
    model = Favorito
    titulo = "Mi Favorito"
    form_class = UsrMainForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["toolbar"] = crud_toolbar(
            self.request.user, self.object,
            blinder_model="mine_fav",
            qs=self.request.user.mis_favoritos.all())
        return context


class UsrCreate(GenericCreate):
    model = Favorito
    titulo = "Mi Favorito"
    form_class = UsrMainForm

    def get_initial(self):
        initial = super().get_initial().copy()
        initial['user'] = self.request.user.pk
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("mine_fav_read", kwargs={"pk": self.object.pk})


class UsrUpdate(GenericUpdate):
    model = Favorito
    titulo = "Mi Favorito"
    form_class = UsrMainForm

    def get_success_url(self):
        return reverse("mine_fav_read", kwargs={"pk": self.object.pk})


class UsrDelete(GenericDelete):
    model = Favorito

    def get_success_url(self):
        return reverse("mine_fav_list")


class UsrDeleteMany(GenericDeleteMany):
    model = Favorito


class UsrGetList(UsrList):
    template_name = "igs_app_favorito/favorito_get_list.html"


class UsrAddFav(UsrGetList):

    def do_action(self):
        self.model.objects.get_or_create(
            user=self.request.user,
            etiqueta=get_from_request(self.request, 'etiqueta'),
            url=get_from_request(self.request, 'url'))

    def get(self, *args, **kwargs):
        self.do_action()
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class UsrDeleteFav(UsrGetList):

    def do_action(self):
        self.model.objects.filter(
            user=self.request.user,
            url=get_from_request(self.request, 'url')).delete()

    def get(self, *args, **kwargs):
        self.do_action()
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)
