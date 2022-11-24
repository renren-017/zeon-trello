from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404

from .models import *
from .forms import BarForm, CommentForm, labelFormset


class BoardListView(LoginRequiredMixin, ListView):
    login_url = 'accounts/login/'
    template_name = 'boards/board_list.html'

    def get_queryset(self):
        return Board.objects.filter(members__id=self.request.user.pk)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_boards'] = self.get_queryset().order_by('-last_modified')[:6]
        context['starred_boards'] = self.get_queryset().filter(is_starred=True)
        context['archived_boards'] = self.get_queryset().filter(is_active=False)
        return context


class BoardCreateView(CreateView):
    model = Board
    fields = ["title", "background_img"]

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        form.instance.save()
        form.instance.members.add(self.request.user)
        return super().form_valid(form)


class BoardDetailView(DetailView, LoginRequiredMixin, FormMixin):
    login_url = reverse_lazy('login')
    model = Board
    template_name = 'boards/board_detail.html'
    context_object_name = 'board'
    form_class = BarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bars'] = Bar.objects.all()
        context['form'] = BarForm(initial={'board_id': self.object.id})
        return context

    def get_success_url(self):
        return reverse('post-detail', kwargs={'pk': self.object.id})

    def post(self, request, pk):
        board = get_object_or_404(Board, pk=pk)
        form = BarForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.board = board
            obj.save()
            return redirect('board-detail', board.pk)

    def form_valid(self, form):
        form.save()
        return super(BoardDetailView, self).form_valid(form)


class CardCreateView(CreateView):
    model = Card
    fields = [
        "title",
        "description",
        "deadline",
    ]

    def form_valid(self, form):
        form.instance.bar = Bar.objects.get(id=self.kwargs['bar_id'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["board_id"] = self.kwargs['board_id']
        return context

    def get_success_url(self):
        return reverse("board-detail", kwargs={'pk': self.kwargs['board_id']})


class CardUpdateView(UpdateView):
    model = Card
    fields = [
        "title",
        "description",
        "deadline",
    ]

    def form_valid(self, form):
        form.instance.bar = self.object.bar
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["board_id"] = self.kwargs['board_id']
        context["labels"] = labelFormset(instance=self.get_object())
        return context

    def get_success_url(self):
        return redirect(reverse('card-detail', kwargs={'board_id': self.kwargs['board_id'],
                                                       'bar_id': self.get_object().bar.id,
                                                       'pk': self.get_object().pk}))


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
        context['checklists'] = CardCheckList.objects.filter(card=card)
        context['comments'] = CardComment.objects.filter(card=card)
        context['files'] = CardFile.objects.filter(card=card)
        context['form'] = self.get_form()
        return context

    def post(self, request, board_id, bar_id, pk):
        card = get_object_or_404(Card, pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.card = card
            obj.user = self.request.user
            obj.save()
            return redirect(reverse('card-detail', kwargs={'board_id': board_id,
                                              'bar_id': bar_id,
                                              'pk': pk}))