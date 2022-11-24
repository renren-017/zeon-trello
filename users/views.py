from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.contrib.auth import get_user_model, login
from django.views.generic import CreateView, RedirectView, TemplateView

from .token import account_activation_token
from .forms import MyUserCreationForm


class SignUpView(CreateView):
    form_class = MyUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('check_email')

    def form_valid(self, form):
        to_return = super().form_valid(form)

        user = form.save()
        user.is_active = False
        user.save()

        current_site = get_current_site(self.request)
        mail_subject = 'Activation link has been sent'
        message = render_to_string('users/acc_activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data['email']

        email = EmailMessage(
            mail_subject, message, to=(to_email,)
        )

        email.send()

        return to_return


class ActivateView(RedirectView):
    url = reverse_lazy('success')

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model()
            current_user = user.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, user.DoesNotExist):
            current_user = None

        if user is not None and account_activation_token.check_token(current_user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return super().get(request, uidb64, token)
        else:
            return render(request, 'users/invalid_acc_activation.html')


class CheckEmailView(TemplateView):
    template_name = 'users/check_email.html'


class SuccessView(TemplateView):
    template_name = 'users/success.html'
