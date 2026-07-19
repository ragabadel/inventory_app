from __future__ import annotations

from collections.abc import Iterable

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.utils.translation import gettext as _


class CustomPermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Enforce Django permissions and the configured permission-group rules.

    ``permission_required`` may be a single permission or an iterable. Both
    fully-qualified permissions (``inventory.change_itasset``) and codenames
    (``change_itasset``) are supported.
    """

    permission_required: str | Iterable[str] | None = None

    @staticmethod
    def _codename(permission: str) -> str:
        return permission.rsplit(".", 1)[-1]

    @classmethod
    def _pattern_matches(cls, pattern: str, permission: str) -> bool:
        codename = cls._codename(permission)
        if pattern == "*":
            return True

        pattern_codename = cls._codename(pattern)
        if pattern_codename.endswith("*"):
            return codename.startswith(pattern_codename[:-1])

        return pattern == permission or pattern_codename == codename

    def get_permission_required(self) -> tuple[str, ...]:
        required = self.permission_required
        if not required:
            return ()
        if isinstance(required, str):
            return (required,)
        return tuple(required)

    def get_user_group_rules(self) -> dict[str, set[str]]:
        if self.request.user.is_superuser:
            return {"can": {"*"}, "cannot": set()}

        can_permissions: set[str] = set()
        cannot_permissions: set[str] = set()

        for group in self.request.user.groups.all():
            config = settings.PERMISSION_GROUPS.get(group.name, {})
            can_permissions.update(config.get("can", []))
            cannot_permissions.update(config.get("cannot", []))

        return {"can": can_permissions, "cannot": cannot_permissions}

    def check_permission(self, permission: str) -> bool:
        user = self.request.user
        if user.is_superuser:
            return True

        # Prefer Django's native permission framework when a full permission
        # name is provided. The configured group rules remain supported for
        # legacy groups that were created without Django Permission records.
        if "." in permission and user.has_perm(permission):
            return True

        rules = self.get_user_group_rules()
        if any(self._pattern_matches(pattern, permission) for pattern in rules["cannot"]):
            return False

        return any(self._pattern_matches(pattern, permission) for pattern in rules["can"])

    def test_func(self) -> bool:
        required = self.get_permission_required()
        if not required:
            return False
        return all(self.check_permission(permission) for permission in required)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        group_info = []
        for group in self.request.user.groups.all():
            config = settings.PERMISSION_GROUPS.get(group.name, {})
            group_info.append(
                {
                    "name": group.name,
                    "description": config.get("description", ""),
                    "can": config.get("can", []),
                    "cannot": config.get("cannot", []),
                }
            )

        messages.error(self.request, _("You don't have permission to access this page."))
        return render(
            self.request,
            "403.html",
            {
                "groups": group_info,
                "required_permissions": self.get_permission_required(),
            },
            status=403,
        )


class ReadOnlyMixin(CustomPermissionMixin):
    """Require the configured view permission for read-only views."""

    pass


class NoDeleteMixin(CustomPermissionMixin):
    """Require an explicit delete permission for Django DeleteView requests."""

    def test_func(self) -> bool:
        model = getattr(self, "model", None)
        if model is None:
            return super().test_func()

        permission = self.permission_required or (
            f"{model._meta.app_label}.delete_{model._meta.model_name}"
        )

        if self.request.method in {"POST", "DELETE"}:
            operation = f"delete_{model._meta.model_name}"
            if operation in getattr(settings, "CRITICAL_OPERATIONS", []):
                return self.request.user.is_superuser
            return self.check_permission(permission)

        # A GET request may render the confirmation page, but it still requires
        # the same delete permission so the URL cannot be used to discover
        # protected records.
        return self.check_permission(permission)
