from django.shortcuts import redirect

from online_school_site import settings


def anonymous_required(func):
    def as_view(request, *args, **kwargs):
        redirect_to = kwargs.get('redirect', settings.HOME_URL)
        if request.user.is_authenticated:
            return redirect(redirect_to)

        return func(request, *args, **kwargs)

    return as_view

