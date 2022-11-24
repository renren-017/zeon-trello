from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse

from .models import *
from .forms import CardLabelForm


class CardLabelCreateView(CreateView):
    model = CardLabel
    form_class = CardLabelForm
    template_name = 'boards/asset_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["board_id"] = self.kwargs['board_id']
        return context

    def form_valid(self, form):
        form.instance.card = Card.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('card-detail', kwargs={'board_id': self.kwargs['board_id'],
                                              'bar_id': self.kwargs['bar_id'],
                                              'pk': self.kwargs['pk']})


class CardFileCreateView(CreateView):
    model = CardFile
    template_name = 'boards/asset_form.html'
    fields = [
        'file'
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["board_id"] = self.kwargs['board_id']
        return context

    def form_valid(self, form):
        form.instance.card = Card.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('card-detail', kwargs={'board_id': self.kwargs['board_id'],
                                              'bar_id': self.kwargs['bar_id'],
                                              'pk': self.kwargs['pk']})


class CardChecklistCreateView(CreateView):
    model = CardChecklistItem
    template_name = 'boards/asset_form.html'
    fields = [
        'content'
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["board_id"] = self.kwargs['board_id']
        return context

    def form_valid(self, form):
        form.instance.card = Card.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('card-detail', kwargs={'board_id': self.kwargs['board_id'],
                                              'bar_id': self.kwargs['bar_id'],
                                              'pk': self.kwargs['pk']})
