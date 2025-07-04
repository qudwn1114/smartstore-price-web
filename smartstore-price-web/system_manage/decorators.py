from django.shortcuts import redirect, resolve_url
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponse

# 권한 체크
def permission_required(redirect_url=None, raise_exception=False):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if 'system-manage' in request.path:
                if not user.is_authenticated:
                    if raise_exception:
                        return HttpResponse('Unauthorized', status=401)
                    else:
                        return redirect(f"{resolve_url('system_manage:login')}?next={request.path}")
                if user.is_superuser:
                    pass
                else:
                    if raise_exception:
                        raise PermissionDenied()
                    else:
                        next_url = request.get_full_path()
                        path = resolve_url(redirect_url)
                        return redirect(f'{path}?next={next_url}')
            return function(request, *args, **kwargs)
        return wrapper
    return decorator