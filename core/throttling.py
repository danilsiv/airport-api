from rest_framework.throttling import SimpleRateThrottle, UserRateThrottle


class AdminRateThrottle(SimpleRateThrottle):
    scope = "staff"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_staff:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident
        }


class CustomUserRateThrottle(SimpleRateThrottle):
    scope = "user"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_staff:
            return None
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident
        }
