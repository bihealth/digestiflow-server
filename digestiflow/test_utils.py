from projectroles.models import Project, SODAR_CONSTANTS, Role, RoleAssignment


class SetupUserMixin:
    def setUp(self):
        super().setUp()
        self.user = self.make_user()

    def make_user(self, *args, **kwargs):
        is_super_user = kwargs.pop("is_super_user", False)
        result = super().make_user(*args, **kwargs)
        if is_super_user:
            result.is_superuser = True
            result.save()
        return result


class SetupProjectMixin:
    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(
            title="Test project", type=SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]
        )
        # Setup users and role assignments
        self.root = self.make_user(username="root", is_super_user=True)
        self.owner = self.make_user(username="owner")
        RoleAssignment.objects.create(
            project=self.project,
            user=self.owner,
            role=Role.objects.get(name=SODAR_CONSTANTS["PROJECT_ROLE_OWNER"]),
        )
        self.delegate = self.make_user(username="delegate")
        RoleAssignment.objects.create(
            project=self.project,
            user=self.delegate,
            role=Role.objects.get(name=SODAR_CONSTANTS["PROJECT_ROLE_DELEGATE"]),
        )
        self.contributor = self.make_user(username="contributor")
        RoleAssignment.objects.create(
            project=self.project,
            user=self.contributor,
            role=Role.objects.get(name=SODAR_CONSTANTS["PROJECT_ROLE_CONTRIBUTOR"]),
        )
        self.guest = self.make_user(username="guest")
        RoleAssignment.objects.create(
            project=self.project,
            user=self.guest,
            role=Role.objects.get(name=SODAR_CONSTANTS["PROJECT_ROLE_GUEST"]),
        )
        self.norole = self.make_user(username="norole")
        # Another project's owner
        self.unrelated_owner = self.make_user(username="unrelated_owner")
        self.unrelated_project = Project.objects.create(
            title="Unrelated project", type=SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]
        )
        RoleAssignment.objects.create(
            project=self.unrelated_project,
            user=self.unrelated_owner,
            role=Role.objects.get(name=SODAR_CONSTANTS["PROJECT_ROLE_OWNER"]),
        )

    def runGet(self, user, project=None, **kwargs):
        return super().runGet(
            user, self.url_name, project=(project or self.project).sodar_uuid, **kwargs
        )

    def runPost(self, user, data, project=None, **kwargs):
        return super().runPost(
            user, self.url_name, project=(project or self.project).sodar_uuid, data=data, **kwargs
        )

    def runPut(self, user, data, project=None, **kwargs):
        return super().runPut(
            user, self.url_name, project=(project or self.project).sodar_uuid, data=data, **kwargs
        )

    def runDelete(self, user, project=None, **kwargs):
        return super().runDelete(
            user, self.url_name, project=(project or self.project).sodar_uuid, **kwargs
        )


class AuthenticatedRequestMixin:
    """Mixin with test helper functions"""

    def runGet(self, user, url_name, *args, **kwargs):
        def func():
            return self.get(url_name, *args, follow=True, **kwargs)

        if user:
            with self.login(user):
                return func()
        else:
            return func()

    def runPost(self, user, url_name, *args, **kwargs):
        def func():
            return self.post(url_name, *args, follow=True, **kwargs)

        if user:
            with self.login(user):
                return func()
        else:
            return func()

    def runPut(self, user, url_name, *args, **kwargs):
        def func():
            return self.put(url_name, *args, follow=True, **kwargs)

        if user:
            with self.login(user):
                return func()
        else:
            return func()

    def runDelete(self, user, url_name, *args, **kwargs):
        def func():
            return self.delete(url_name, *args, follow=True, **kwargs)

        if user:
            with self.login(user):
                return func()
        else:
            return func()

    def assertUnauthorizedRedirect(
        self, user, response, target_url="/", message_token="not authorized"
    ):
        if user is None:
            self.assertTrue(
                response.redirect_chain[-1][0].startswith("/login/?next="), "user=%s" % user
            )
        else:
            self.assertRedirects(
                response, target_url, fetch_redirect_response=True, msg_prefix="user=%s" % user
            )
            self.assertIn(message_token, str(list(response.context.get("messages"))[0]))
