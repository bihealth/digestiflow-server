"""The views for the fileboxes app."""

import re

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from projectroles.plugins import get_backend_api
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin

from .forms import FileBoxForm, FileBoxGrantForm, FileBoxRevokeForm
from .models import FileBox


class FileBoxListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of all FileBox records"""

    template_name = "fileboxes/filebox_list.html"
    permission_required = "fileboxes.view_data"

    model = FileBox
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])


class FileBoxDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display detail of FileBox records"""

    template_name = "fileboxes/filebox_detail.html"
    permission_required = "fileboxes.view_data"

    model = FileBox

    slug_url_kwarg = "filebox"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["grant_form"] = FileBoxGrantForm()
        return result


class FileBoxCreateView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    CreateView,
):
    """Display list of all FileBox records"""

    success_message = "File box successfully created."
    template_name = "fileboxes/filebox_create.html"
    permission_required = "fileboxes.add_data"

    model = FileBox
    form_class = FileBoxForm

    def get_form_kwargs(self, *args, **kwargs):
        result = super().get_form_kwargs(*args, **kwargs)
        result.setdefault("project", self.get_project())
        return result

    @transaction.atomic
    def form_valid(self, form):
        """Automatically set the project property."""
        # Create the sequencing machine.
        form.instance.project = self.get_project(self.request, self.kwargs)
        result = super().form_valid(form)
        # Add audit trail event.
        form.instance.fileboxauditentry_set.create(
            actor=self.request.user,
            action="CREATE",
            message="created new file box '%s'" % form.instance.title,
        )
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="fileboxes",
                user=self.request.user,
                event_name="filebox_create",
                description="create filebox {filebox}",
                status_type="OK",
            )
            tl_event.add_object(obj=self.object, label="filebox", name=self.object.title)
        return result


class FileBoxUpdateView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Updating of FileBox records"""

    success_message = "File box successfully updated."
    template_name = "fileboxes/filebox_update.html"
    permission_required = "fileboxes.change_data"

    model = FileBox
    form_class = FileBoxForm

    slug_url_kwarg = "filebox"
    slug_field = "sodar_uuid"

    def form_valid(self, form):
        with transaction.atomic():
            old_object = FileBox.objects.get(id=self.object.id)
            print("FORM VALID")
            if getattr(old_object, "state_meta") != form.cleaned_data["state_meta"]:
                self._register_state_change(
                    "state_meta", getattr(old_object, "state_meta"), form.cleaned_data["state_meta"]
                )
            changed = []
            for field in ("title", "description", "date_frozen", "date_expiry"):
                if getattr(old_object, field) != form.cleaned_data[field]:
                    changed.append((field, getattr(old_object, field), form.cleaned_data[field]))
            if changed:
                self._register_attr_changes(changed)
        return super().form_valid(form)

    def _register_state_change(self, field, prv, nxt):
        old_object = FileBox.objects.get(id=self.object.id)
        old_object.update_state_meta(self.request.user, field, nxt)

    def _register_attr_changes(self, changes):
        # Add audit trail event.
        changes_str = ", ".join(
            ["'%s': '%s' -> '%s'" % tuple(map(str, change)) for change in changes]
        )
        self.object.fileboxauditentry_set.create(
            actor=self.request.user,
            action="UPDATE_ATTRS",
            message="updated attributes of file box '%s': %s" % (self.object.title, changes_str),
        )
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="fileboxes",
                user=self.request.user,
                event_name="filebox_update_attrs",
                description="updating attributes of file box {filebox}",
                status_type="OK",
            )
            tl_event.add_object(obj=self.object, label="filebox", name=self.object.title)

    def get_form_kwargs(self, *args, **kwargs):
        result = super().get_form_kwargs(*args, **kwargs)
        result.setdefault("project", self.get_project())
        return result


class FileBoxDeleteView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DeleteView,
):
    """Deletion of FileBox records"""

    success_message = "File box successfully deactivated."
    template_name = "fileboxes/filebox_confirm_delete.html"
    permission_required = "fileboxes.delete_data"

    model = FileBox

    slug_url_kwarg = "filebox"
    slug_field = "sodar_uuid"

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Do not delete, just deactivate.
        self.object = self.get_object()
        if self.object.state_meta == "DELETED":
            return redirect(self.get_success_url())
        else:
            self.object.state_meta = "DELETED"
            self.object.save()
        # Add audit trail event.
        self.object.fileboxauditentry_set.create(
            actor=self.request.user,
            action="UPDATE_STATE",
            message="deactivated file box '%s'" % self.object.title,
        )
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="fileboxes",
                user=self.request.user,
                event_name="filebox_delete",
                description="deactivating file box {filebox}",
                status_type="OK",
            )
            tl_event.add_object(obj=self.object, label="filebox", name=self.object.title)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "fileboxes:filebox-list",
            kwargs={"project": self.get_project(self.request, self.kwargs).sodar_uuid},
        )


class FileBoxGrantView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    template_name = "fileboxes/filebox_detail.html"
    permission_required = "fileboxes.update_data"

    model = FileBox
    form_class = FileBoxGrantForm

    slug_url_kwarg = "filebox"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["grant_form"] = result["form"]
        return result

    def _form_valid_ldap(self, accounts):
        """Handle valid form if LDAP is available"""
        preexisting_accounts = []
        created_accounts = []
        bad_accounts = []

        # import pdb; pdb.set_trace()

        ldap_conns = []
        if settings.ENABLE_LDAP:
            import ldap  # noqa

            ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            ldap_conn.set_option(ldap.OPT_REFERRALS, 0)
            ldap_conn.set_option(ldap.OPT_TIMEOUT, 5)
            ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
            ldap_conns.append((settings.AUTH_LDAP_USERNAME_DOMAIN, ldap_conn))
        if settings.ENABLE_LDAP_SECONDARY:
            import ldap  # noqa

            ldap_conn = ldap.initialize(settings.AUTH_LDAP2_SERVER_URI)
            ldap_conn.set_option(ldap.OPT_REFERRALS, 0)
            ldap_conn.set_option(ldap.OPT_TIMEOUT, 5)
            ldap_conn.simple_bind_s(settings.AUTH_LDAP2_BIND_DN, settings.AUTH_LDAP2_BIND_PASSWORD)
            ldap_conns.append((settings.AUTH_LDAP2_USERNAME_DOMAIN, ldap_conn))

        with transaction.atomic():
            for account in accounts:
                for domain, conn in ldap_conns:
                    search_filter = "(|(mail=%s)(userPrincipalName=%s))" % (account, account)
                    if account.endswith("@%s" % domain):
                        search_filter = "(|%s(sAMAccountName=%s))" % (
                            search_filter,
                            account[: -len(domain) - 1],
                        )
                    results = conn.search_s(
                        settings.AUTH_LDAP_USER_SEARCH_BASE,
                        ldap.SCOPE_SUBTREE,
                        search_filter,
                        ["sAMAccountName", "userPrincipalName", "displayName", "mail"],
                    )
                    if results:
                        record_dn, record = results[0]
                        username = "%s@%s" % (record["sAMAccountName"][0].decode("utf-8"), domain)
                        full_name = record["displayName"][0].decode("utf-8")
                        email = record["mail"][0].decode("utf-8")
                        if self.object.fileboxaccountgrant_set.filter(
                            Q(username=username) | Q(email=email)
                        ):
                            preexisting_accounts.append(account)
                        else:
                            self._grant_user(
                                username=username, full_name=full_name, email=email,
                            )
                            created_accounts.append(account)
                        break
                    else:
                        bad_accounts.append(account)

        return preexisting_accounts, created_accounts, bad_accounts

    def _form_valid_noldap(self, accounts):
        """Handle valid form if LDAP is not available"""
        bad_accounts = [a for a in accounts if len(a) <= 3]
        good_accounts = [a for a in accounts if len(a) > 3]
        created_accounts = []
        preexisting_accounts = []
        with transaction.atomic():
            for account in good_accounts:
                if self.object.fileboxaccountgrant_set.filter(username=account):
                    preexisting_accounts.append(account)
                else:
                    self._grant_user(username=account)
                    created_accounts.append(account)
        return preexisting_accounts, created_accounts, bad_accounts

    def _grant_user(self, username, full_name=None, email=None):
        self.object.fileboxauditentry_set.create(
            actor=self.request.user,
            action="ADD_MEMBER",
            message="adding member '%s' to file box '%s'" % (username, self.object.title),
        )
        self.object.fileboxaccountgrant_set.create(
            username=username, full_name=full_name, email=email
        )
        # Register event with timeline.
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="fileboxes",
                user=self.request.user,
                event_name="filebox_grant",
                description="granting access for %s to box {filebox}" % username,
                status_type="OK",
            )
            tl_event.add_object(obj=self.object, label="filebox", name=self.object.title)

    def form_valid(self, form):
        accounts = [x for x in re.split(r"[\s,;]+", form.cleaned_data["users"]) if x]
        if settings.ENABLE_LDAP:
            preexisting_accounts, created_accounts, bad_accounts = self._form_valid_ldap(accounts)
        else:
            preexisting_accounts, created_accounts, bad_accounts = self._form_valid_noldap(accounts)
        if preexisting_accounts:
            messages.add_message(
                self.request,
                messages.WARNING,
                "The following accounts have already been granted access: %s"
                % ", ".join(preexisting_accounts),
            )
        if created_accounts:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "Successfully granted access to: %s" % ", ".join(created_accounts),
            )
        if bad_accounts:
            if settings.ENABLE_LDAP:
                reason = "not found"
            else:
                reason = "too short"
            messages.add_message(
                self.request,
                messages.WARNING,
                "Ignoring accounts (%s): %s" % (reason, ", ".join(bad_accounts)),
            )
        return redirect(
            "fileboxes:filebox-detail",
            project=self.object.project.sodar_uuid,
            filebox=self.object.sodar_uuid,
        )


class FileBoxRevokeView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    template_name = "fileboxes/filebox_confirm_revoke.html"
    permission_required = "fileboxes.update_data"

    model = FileBox
    form_class = FileBoxRevokeForm

    slug_url_kwarg = "filebox"
    slug_field = "sodar_uuid"

    def _get_grant(self):
        return self.object.fileboxaccountgrant_set.filter(
            sodar_uuid=self.request.GET.get("grant")
        ).first()

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["grant"] = self._get_grant()
        return result

    def form_valid(self, form):
        with transaction.atomic():
            grant = self._get_grant()
            self.object.fileboxauditentry_set.create(
                actor=self.request.user,
                action="REMOVE_MEMBER",
                message="removing member '%s' from file box '%s'"
                % (grant.username, self.object.title),
            )
            grant.delete()
            # Register event with timeline.
            timeline = get_backend_api("timeline_backend")
            if timeline:
                tl_event = timeline.add_event(
                    project=self.get_project(self.request, self.kwargs),
                    app_name="fileboxes",
                    user=self.request.user,
                    event_name="filebox_revoke",
                    description="revoking access for %s to box {filebox}" % grant.username,
                    status_type="OK",
                )
                tl_event.add_object(obj=self.object, label="filebox", name=self.object.title)
        messages.add_message(
            self.request, messages.SUCCESS, "Successfully revoked access from: %s" % grant.username,
        )
        return redirect(
            "fileboxes:filebox-detail",
            project=self.object.project.sodar_uuid,
            filebox=self.object.sodar_uuid,
        )
