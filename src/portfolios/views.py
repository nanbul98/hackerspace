import os
from comments.models import Document
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User

from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from portfolios.forms import PortfolioForm, ArtworkForm
from portfolios.models import Portfolio, Artwork


@method_decorator(login_required, name='dispatch')
class PortfolioList(ListView):
    model = Portfolio
    template_name = 'portfolios/list.html'


@method_decorator(login_required, name='dispatch')
class PortfolioCreate(CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'portfolios/form.html'

    def form_valid(self, form):
        data = form.save(commit=False)
        data.user = self.request.user
        data.save()
        return super(PortfolioCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PortfolioCreate, self).get_context_data(**kwargs)
        context['heading'] = "Create " + self.request.user.get_username() + "'s Portfolio"
        context['action_value'] = ""
        context['submit_btn_value'] = "Create"
        return context


@method_decorator(login_required, name='dispatch')
class PortfolioDetail(DetailView):
    model = Portfolio

    def dispatch(self, *args, **kwargs):
        # only allow admins or the users to see their own portfolios, unless they are shared
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs.get('pk'))
        if portfolio.listed_locally or portfolio.user == self.request.user or self.request.user.is_staff:
            return super(PortfolioDetail, self).dispatch(*args, **kwargs)
        else:
            raise Http404("Sorry, this portfolio isn't shared!")


@login_required
def detail(request, pk=None):

    if pk is None:
        pk = request.user.id
    user = get_object_or_404(User, id=pk)
    p, created = Portfolio.objects.get_or_create(user=user)

    # only allow admins or the users to see their own portfolios, unless they are shared
    if request.user.is_staff or p.pk == request.user.id or p.listed_locally:
        context = {
            "p": p,
        }
        return render(request, 'portfolios/detail.html', context)
    else:
        raise Http404("Sorry, this portfolio isn't shared!")


def public_list(request):
    public_portfolios = Portfolio.objects.all().filter(listed_publicly=True)
    return render(request, 'portfolios/public_list.html', {"portfolios": public_portfolios})


def public(request, uuid):
    p = get_object_or_404(Portfolio, uuid=uuid)
    return render(request, 'portfolios/public.html', {"p": p})


@login_required
def edit(request, pk=None):

    # portfolio pk is portfolio.user.id
    if pk is None:
        pk = request.user.id
    user = get_object_or_404(User, id=pk)
    p = get_object_or_404(Portfolio, user=user)

    # if user submitted the Portfolio form to make changes:
    form = PortfolioForm(request.POST or None, instance=p)
    if form.is_valid():
        form.save()
        messages.success(request, "Portfolio updated.")

    # only allow admins or the users to edit their own portfolios
    if request.user.is_staff or request.user == p.user:
        context = {
            "p": p,
            "form": form,
        }
        return render(request, 'portfolios/edit.html', context)
    else:
        raise Http404("Sorry, this portfolio isn't yours!")


######################################
#
#         ARTWORK VIEWS
#
######################################

@method_decorator(login_required, name='dispatch')
class ArtworkCreate(SuccessMessageMixin, CreateView):
    model = Artwork
    form_class = ArtworkForm
    template_name = 'portfolios/art_form.html'
    success_message = "The art was added to the Portfolio"

    def get_success_url(self):
        return reverse('portfolios:edit', kwargs={'pk': self.object.portfolio.pk})

    def form_valid(self, form):
        data = form.save(commit=False)
        data.portfolio = get_object_or_404(Portfolio, pk=self.kwargs.get('pk'))
        data.save()
        return super(ArtworkCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ArtworkCreate, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs.get('pk'))
        context['heading'] = "Add Art to " + portfolio.user.get_username() + "'s Portfolio"
        context['action_value'] = ""
        context['submit_btn_value'] = "Create"
        context['portfolio'] = portfolio
        return context

    def dispatch(self, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs.get('pk'))
        # only allow the user or staff to edit
        if portfolio.user == self.request.user or self.request.user.is_staff:
            return super(ArtworkCreate, self).dispatch(*args, **kwargs)
        else:
            raise Http404("Sorry, this isn't your portfolio!")


@method_decorator(login_required, name='dispatch')
class ArtworkUpdate(SuccessMessageMixin, UpdateView):
    model = Artwork
    form_class = ArtworkForm
    template_name = 'portfolios/art_form.html'
    success_message = "Art updated!"

    def get_success_url(self):
        return reverse('portfolios:edit', kwargs={'pk': self.object.portfolio.pk})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ArtworkUpdate, self).get_context_data(**kwargs)
        context['heading'] = "Edit " + self.object.portfolio.user.get_username() + "'s Portfolio Art"
        context['action_value'] = ""
        context['submit_btn_value'] = "Update"
        context['portfolio'] = self.object.portfolio
        return context

    def dispatch(self, *args, **kwargs):
        art = get_object_or_404(Artwork, pk=self.kwargs.get('pk'))
        # only allow the user or staff to edit
        if art.portfolio.user == self.request.user or self.request.user.is_staff:
            return super(ArtworkUpdate, self).dispatch(*args, **kwargs)
        else:
            raise Http404("Sorry, this isn't your art!")


@method_decorator(login_required, name='dispatch')
class ArtworkDelete(DeleteView):
    model = Artwork

    def get_success_url(self):
        return reverse('portfolios:edit', kwargs={'pk': self.object.portfolio.pk})


# @login_required
# def art_detail(request, pk):
#     art = get_object_or_404(Artwork, pk=pk)
#     # only allow admins or the users to view
#     if request.user.is_staff or art.portfolio.user == request.user:
#         context = {
#             "art": art,
#         }
#         return render(request, 'portfolios/art_detail.html', context)
#     else:
#         raise Http404("Sorry, this isn't your art!")


@login_required
def art_add(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    doc_user = doc.comment.user
    if request.user.is_staff or doc_user == request.user:
        filename = os.path.basename(doc.docfile.name)
        # Get extension from filename to determine filetype...very hacky...
        img_ext_list = [".png", ".gif", ".jpg"]
        vid_ext_list = [".ogg", ".avi", ".mp4", ".mkv", ".webm", ".ogv"]
        name, ext = os.path.splitext(filename)

        if ext in img_ext_list:
            image_file = doc.docfile
            video_file = None
        elif ext in vid_ext_list:
            image_file = None
            video_file = doc.docfile
        else:
            raise Http404("Unsupported image or video format.  See your teacher if"
                          " you think this format should be supported.")
        # TODO: WHY IS THIS A TUPLE?!
        portfolio = doc_user.portfolio,
        portfolio = portfolio[0]

        Artwork.create(
            title=name,
            image_file=image_file,
            video_file=video_file,
            portfolio=portfolio,
            date=doc.comment.timestamp.date(),
        )
        return redirect('portfolios:detail', pk=portfolio.pk)
    else:
        raise Http404("I don't think you're supposed to be here....")


