from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse

from .models import *
from .forms import CardLabelForm


class CardMarkCreateView(CreateView):
    model = Mark
    form_class = CardLabelForm
    template_name = 'boards/asset_form.html'

    def form_valid(self, form):
        card = Card.objects.get(id=self.kwargs['pk'])
        form.instance.board = card.column.board
        form.instance.save()
        CardMark(mark=form.instance, card=card).save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('card-detail', kwargs={'pk': self.kwargs['pk']})


class CardFileCreateView(CreateView):
    model = CardFile
    template_name = 'boards/asset_form.html'
    fields = [
        'file'
    ]

    def form_valid(self, form):
        form.instance.card = Card.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('card-detail', kwargs={'pk': self.kwargs['pk']})


# class CardChecklistCreateView(CreateView):
#     model = CardChecklistItem
#     template_name = 'boards/asset_form.html'
#     fields = [
#         'content'
#     ]
#
#     def form_valid(self, form):
#         form.instance.card = Card.objects.get(id=self.kwargs['pk'])
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse('card-detail', kwargs={'pk': self.kwargs['pk']})
#
#
class CardCommentCreateView(CreateView):
    model = CardComment
    template_name = 'boards/asset_form.html'
    fields = [
        'body'
    ]

    def form_valid(self, form):
        form.instance.card = Card.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('card-detail', kwargs={'pk': self.kwargs['pk']})
