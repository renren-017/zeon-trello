from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q

from .models import *
from .forms import BarForm, CommentForm, labelFormset, CardCreateForm, CardUpdateForm


class BoardListView(LoginRequiredMixin, ListView):
    login_url = 'accounts/login/'
    template_name = 'boards/board_list.html'

    def get_queryset(self):
        return Board.objects.filter(members__id=self.request.user.pk)


class BoardCreateView(CreateView):
    model = Board
    fields = ["title", "background_img"]
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        form.instance.members.add(self.request.user)
        return super().form_valid(form)


class BoardUpdateView(UpdateView):
    model = Board
    fields = ["title", "background_img", "is_starred", "is_active", "members"]

    def get_success_url(self):
        return reverse("board-detail", kwargs={'pk': self.kwargs['pk']})


class BoardDeleteView(DeleteView):
    model = Board
    template_name = 'boards/delete_form.html'
    success_url = reverse_lazy("home")


class BoardDetailView(DetailView, LoginRequiredMixin, FormMixin):
    login_url = reverse_lazy('login')
    model = Board
    template_name = 'boards/board_detail.html'
    context_object_name = 'board'
    form_class = BarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bars'] = Bar.objects.filter(board=self.object)
        context['form'] = BarForm(initial={'board_id': self.object.id})
        return context

    def post(self, request, pk):
        board = get_object_or_404(Board, pk=pk)
        form = BarForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.board = board
            obj.save()
            return redirect('board-detail', board.pk)


class CardCreateView(CreateView):
    model = Card
    form_class = CardCreateForm

    def form_valid(self, form):
        form.instance.bar = Bar.objects.get(id=self.kwargs['bar_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("board-detail", kwargs={'pk': self.kwargs['board_id']})


class CardUpdateView(UpdateView):
    model = Card
    form_class = CardUpdateForm
    context_object_name = 'card'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["labels"] = labelFormset(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse('card-detail', kwargs={'pk': self.get_object().pk})


class CardDetailView(DetailView, LoginRequiredMixin, FormMixin):
    model = Card
    template_name = 'boards/card_detail.html'
    context_object_name = 'card'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        card = self.get_object()
        context = super().get_context_data(**kwargs)
        context["board_id"] = card.bar.board.id
        context['labels'] = CardLabel.objects.filter(card=card)
        context['checklists'] = CardChecklistItem.objects.filter(card=card)
        context['comments'] = CardComment.objects.filter(card=card)
        context['files'] = CardFile.objects.filter(card=card)
        context['form'] = self.get_form()
        return context

    def post(self, request, pk):
        card = get_object_or_404(Card, pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.card = card
            obj.user = self.request.user
            obj.save()
            return redirect(reverse('card-detail', kwargs={'pk': pk}))


class CardDeleteView(DeleteView):
    model = Card
    template_name = 'boards/delete_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["board_id"] = self.get_object().bar.board.pk
        return context

    def get_success_url(self, **kwargs):
        return reverse('board-detail', kwargs={'pk': self.get_context_data()['board_id']})


class SearchResultsView(ListView):
    model = Board
    template_name = 'boards/board_list.html'

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = Board.objects.filter(
            Q(title__icontains=query) & Q(members__id=self.request.user.pk)
        )
        return object_list
