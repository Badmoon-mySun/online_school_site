from django.http import Http404
from django.shortcuts import redirect

from main.models import TestHistory
from online_school_site import settings


def anonymous_required(func):
    def as_view(request, *args, **kwargs):
        redirect_to = kwargs.get('redirect', settings.HOME_URL)
        if request.user.is_authenticated:
            return redirect(redirect_to)

        return func(request, *args, **kwargs)

    return as_view


def test_not_finished_required(func):
    def as_view(request, *args, **kwargs):
        user = request.user
        test = TestHistory.objects.filter(user=user)
        if test:
            raise Http404

        return func(request, *args, **kwargs)

    return as_view