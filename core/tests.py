#
# Copyright 2023 © AE UTBM
# ae@utbm.fr / ae.info@utbm.fr
#
# This file is part of the website of the UTBM Student Association (AE UTBM),
# https://ae.utbm.fr.
#
# You can find the source code of the website at https://github.com/ae-utbm/sith3
#
# LICENSED UNDER THE GNU GENERAL PUBLIC LICENSE VERSION 3 (GPLv3)
# SEE : https://raw.githubusercontent.com/ae-utbm/sith3/master/LICENSE
# OR WITHIN THE LOCAL FILE "LICENSE"
#
#

from datetime import date, timedelta
from pathlib import Path
from smtplib import SMTPException

import freezegun
import pytest
from django.core import mail
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import now
from pytest_django.asserts import assertInHTML, assertRedirects

from club.models import Membership
from core.markdown import markdown
from core.models import AnonymousUser, Group, Page, User
from core.utils import get_semester_code, get_start_of_semester
from sith import settings


@pytest.mark.django_db
class TestUserRegistration:
    @pytest.fixture()
    def valid_payload(self):
        return {
            settings.HONEYPOT_FIELD_NAME: settings.HONEYPOT_VALUE,
            "first_name": "this user does not exist (yet)",
            "last_name": "this user does not exist (yet)",
            "email": "i-dont-exist-yet@git.an",
            "password1": "plop",
            "password2": "plop",
            "captcha_0": "dummy-value",
            "captcha_1": "PASSED",
        }

    def test_register_user_form_ok(self, client, valid_payload):
        """Should register a user correctly."""
        assert not User.objects.filter(email=valid_payload["email"]).exists()
        response = client.post(reverse("core:register"), valid_payload)
        assertRedirects(response, reverse("core:index"))
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Création de votre compte AE"
        assert User.objects.filter(email=valid_payload["email"]).exists()

    @pytest.mark.parametrize(
        ("payload_edit", "expected_error"),
        [
            (
                {"password2": "not the same as password1"},
                "Les deux mots de passe ne correspondent pas.",
            ),
            ({"email": "not-an-email"}, "Saisissez une adresse de courriel valide."),
            ({"first_name": ""}, "Ce champ est obligatoire."),
            ({"last_name": ""}, "Ce champ est obligatoire."),
            ({"captcha_1": "WRONG_CAPTCHA"}, "CAPTCHA invalide"),
        ],
    )
    def test_register_user_form_fail(
        self, client, valid_payload, payload_edit, expected_error
    ):
        """Should not register a user correctly."""
        payload = valid_payload | payload_edit
        response = client.post(reverse("core:register"), payload)
        assert response.status_code == 200
        error_html = f'<ul class="errorlist"><li>{expected_error}</li></ul>'
        assertInHTML(error_html, str(response.content.decode()))
        assert not User.objects.filter(email=payload["email"]).exists()

    def test_register_honeypot_fail(self, client: Client, valid_payload):
        payload = valid_payload | {
            settings.HONEYPOT_FIELD_NAME: settings.HONEYPOT_VALUE + "random"
        }
        response = client.post(reverse("core:register"), payload)
        assert response.status_code == 200
        assert not User.objects.filter(email=payload["email"]).exists()

    def test_register_user_form_fail_already_exists(
        self, client: Client, valid_payload
    ):
        """Should not register a user correctly if it already exists."""
        # create the user, then try to create it again
        client.post(reverse("core:register"), valid_payload)
        response = client.post(reverse("core:register"), valid_payload)

        assert response.status_code == 200
        error_html = "<li>Un objet User avec ce champ Adresse email existe déjà.</li>"
        assertInHTML(error_html, str(response.content.decode()))

    def test_register_fail_with_not_existing_email(
        self, client: Client, valid_payload, monkeypatch
    ):
        """Test that, when email is valid but doesn't actually exist, registration fails."""

        def always_fail(*_args, **_kwargs):
            raise SMTPException

        monkeypatch.setattr(EmailMessage, "send", always_fail)

        response = client.post(reverse("core:register"), valid_payload)
        assert response.status_code == 200
        error_html = (
            "<li>Nous n'avons pas réussi à vérifier que cette adresse mail existe.</li>"
        )
        assertInHTML(error_html, str(response.content.decode()))


@pytest.mark.django_db
class TestUserLogin:
    @pytest.fixture()
    def user(self) -> User:
        return User.objects.first()

    def test_login_fail(self, client, user):
        """Should not login a user correctly."""
        response = client.post(
            reverse("core:login"),
            {
                "username": user.username,
                "password": "wrong-password",
                settings.HONEYPOT_FIELD_NAME: settings.HONEYPOT_VALUE,
            },
        )
        assert response.status_code == 200
        assert (
            '<p class="alert alert-red">Votre nom d\'utilisateur '
            "et votre mot de passe ne correspondent pas. Merci de réessayer.</p>"
        ) in str(response.content.decode())

    def test_login_honeypot(self, client, user):
        response = client.post(
            reverse("core:login"),
            {
                "username": user.username,
                "password": "wrong-password",
                settings.HONEYPOT_FIELD_NAME: settings.HONEYPOT_VALUE + "incorrect",
            },
        )
        assert response.status_code == 200
        assert response.wsgi_request.user.is_anonymous

    def test_login_success(self, client, user):
        """Should login a user correctly."""
        response = client.post(
            reverse("core:login"),
            {
                "username": user.username,
                "password": "plop",
                settings.HONEYPOT_FIELD_NAME: settings.HONEYPOT_VALUE,
            },
        )
        assertRedirects(response, reverse("core:index"))
        assert response.wsgi_request.user == user


@pytest.mark.parametrize(
    ("md", "html"),
    [
        (
            "[nom du lien](page://nomDeLaPage)",
            '<a href="/page/nomDeLaPage/">nom du lien</a>',
        ),
        ("__texte__", "<u>texte</u>"),
        ("~~***__texte__***~~", "<del><em><strong><u>texte</u></strong></em></del>"),
        (
            '![tst_alt](/img.png?50% "tst_title")',
            '<img src="/img.png" alt="tst_alt" title="tst_title" style="width:50%;" />',
        ),
        (
            "[texte](page://tst-page)",
            '<a href="/page/tst-page/">texte</a>',
        ),
        (
            "![](/img.png?50x450)",
            '<img src="/img.png" alt="" style="width:50px;height:450px;" />',
        ),
        ("![](/img.png)", '<img src="/img.png" alt="" />'),
        (
            "![](/img.png?50%x120%)",
            '<img src="/img.png" alt="" style="width:50%;height:120%;" />',
        ),
        ("![](/img.png?50px)", '<img src="/img.png" alt="" style="width:50px;" />'),
        (
            "![](/img.png?50pxx120%)",
            '<img src="/img.png" alt="" style="width:50px;height:120%;" />',
        ),
        # when the image dimension has a wrong format, don't touch the url
        ("![](/img.png?50pxxxxxxxx)", '<img src="/img.png?50pxxxxxxxx" alt="" />'),
        ("![](/img.png?azerty)", '<img src="/img.png?azerty" alt="" />'),
    ],
)
def test_custom_markdown_syntax(md, html):
    """Test the homemade markdown syntax."""
    assert markdown(md) == f"<p>{html}</p>\n"


def test_full_markdown_syntax():
    syntax_path = Path(settings.BASE_DIR) / "core" / "fixtures"
    md = (syntax_path / "SYNTAX.md").read_text()
    html = (syntax_path / "SYNTAX.html").read_text()
    result = markdown(md)
    assert result == html


class TestPageHandling(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = User.objects.get(username="root")
        cls.root_group = Group.objects.get(name="Root")

    def setUp(self):
        self.client.force_login(self.root)

    def test_create_page_ok(self):
        """Should create a page correctly."""
        response = self.client.post(
            reverse("core:page_new"),
            {"parent": "", "name": "guy", "owner_group": self.root_group.id},
        )
        self.assertRedirects(
            response, reverse("core:page", kwargs={"page_name": "guy"})
        )
        assert Page.objects.filter(name="guy").exists()

        response = self.client.get(reverse("core:page", kwargs={"page_name": "guy"}))
        assert response.status_code == 200
        html = response.content.decode()
        assert '<a href="/page/guy/hist/">' in html
        assert '<a href="/page/guy/edit/">' in html
        assert '<a href="/page/guy/prop/">' in html

    def test_create_child_page_ok(self):
        """Should create a page correctly."""
        # remove all other pages to make sure there is no side effect
        Page.objects.all().delete()
        self.client.post(
            reverse("core:page_new"),
            {"parent": "", "name": "guy", "owner_group": str(self.root_group.id)},
        )
        page = Page.objects.first()
        self.client.post(
            reverse("core:page_new"),
            {
                "parent": str(page.id),
                "name": "bibou",
                "owner_group": str(self.root_group.id),
            },
        )
        response = self.client.get(
            reverse("core:page", kwargs={"page_name": "guy/bibou"})
        )
        assert response.status_code == 200
        assert '<a href="/page/guy/bibou/">' in str(response.content)

    def test_access_child_page_ok(self):
        """Should display a page correctly."""
        parent = Page(name="guy", owner_group=self.root_group)
        parent.save(force_lock=True)
        page = Page(name="bibou", owner_group=self.root_group, parent=parent)
        page.save(force_lock=True)
        response = self.client.get(
            reverse("core:page", kwargs={"page_name": "guy/bibou"})
        )
        assert response.status_code == 200
        html = response.content.decode()
        self.assertIn('<a href="/page/guy/bibou/edit/">', html)

    def test_access_page_not_found(self):
        """Should not display a page correctly."""
        response = self.client.get(reverse("core:page", kwargs={"page_name": "swagg"}))
        assert response.status_code == 200
        html = response.content.decode()
        self.assertIn('<a href="/page/create/?page=swagg">', html)

    def test_create_page_markdown_safe(self):
        """Should format the markdown and escape html correctly."""
        self.client.post(
            reverse("core:page_new"), {"parent": "", "name": "guy", "owner_group": "1"}
        )
        self.client.post(
            reverse("core:page_edit", kwargs={"page_name": "guy"}),
            {
                "title": "Bibou",
                "content": """Guy *bibou*

http://git.an

# Swag

<guy>Bibou</guy>

<script>alert('Guy');</script>
""",
            },
        )
        response = self.client.get(reverse("core:page", kwargs={"page_name": "guy"}))
        assert response.status_code == 200
        expected = """
            <p>Guy <em>bibou</em></p>
            <p><a href="http://git.an">http://git.an</a></p>
            <h1>Swag</h1>
            <p>&lt;guy&gt;Bibou&lt;/guy&gt;</p>
            <p>&lt;script&gt;alert('Guy');&lt;/script&gt;</p>
            """
        assertInHTML(expected, response.content.decode())


@pytest.mark.django_db
class TestUserTools:
    def test_anonymous_user_unauthorized(self, client):
        """An anonymous user shouldn't have access to the tools page."""
        response = client.get(reverse("core:user_tools"))
        assertRedirects(
            response,
            expected_url=f"/login?next=%2Fuser%2Ftools%2F",
            target_status_code=301,
        )

    @pytest.mark.parametrize("username", ["guy", "root", "skia", "comunity"])
    def test_page_is_working(self, client, username):
        """All existing users should be able to see the test page."""
        # Test for simple user
        client.force_login(User.objects.get(username=username))
        response = client.get(reverse("core:user_tools"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestUserPicture:
    def test_anonymous_user_unauthorized(self, client):
        """An anonymous user shouldn't have access to an user's photo page."""
        response = client.get(
            reverse(
                "core:user_pictures",
                kwargs={"user_id": User.objects.get(username="sli").pk},
            )
        )
        assert response.status_code == 403

    @pytest.mark.parametrize(
        ("username", "status"),
        [
            ("guy", 403),
            ("root", 200),
            ("skia", 200),
            ("sli", 200),
        ],
    )
    def test_page_is_working(self, client, username, status):
        """Only user that subscribed (or admins) should be able to see the page."""
        # Test for simple user
        client.force_login(User.objects.get(username=username))
        response = client.get(
            reverse(
                "core:user_pictures",
                kwargs={"user_id": User.objects.get(username="sli").pk},
            )
        )
        assert response.status_code == status


# TODO: many tests on the pages:
#   - renaming a page
#   - changing a page's parent --> check that page's children's full_name
#   - changing the different groups of the page


class TestFileHandling(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subscriber = User.objects.get(username="subscriber")

    def setUp(self):
        self.client.login(username="subscriber", password="plop")

    def test_create_folder_home(self):
        response = self.client.post(
            reverse("core:file_detail", kwargs={"file_id": self.subscriber.home.id}),
            {"folder_name": "GUY_folder_test"},
        )
        assert response.status_code == 302
        response = self.client.get(
            reverse("core:file_detail", kwargs={"file_id": self.subscriber.home.id})
        )
        assert response.status_code == 200
        assert "GUY_folder_test</a>" in str(response.content)

    def test_upload_file_home(self):
        with open("/bin/ls", "rb") as f:
            response = self.client.post(
                reverse(
                    "core:file_detail", kwargs={"file_id": self.subscriber.home.id}
                ),
                {"file_field": f},
            )
        assert response.status_code == 302
        response = self.client.get(
            reverse("core:file_detail", kwargs={"file_id": self.subscriber.home.id})
        )
        assert response.status_code == 200
        assert "ls</a>" in str(response.content)


class TestUserIsInGroup(TestCase):
    """Test that the User.is_in_group() and AnonymousUser.is_in_group()
    work as intended.
    """

    @classmethod
    def setUpTestData(cls):
        from club.models import Club

        cls.root_group = Group.objects.get(name="Root")
        cls.public = Group.objects.get(name="Public")
        cls.skia = User.objects.get(username="skia")
        cls.toto = User.objects.create(
            username="toto", first_name="a", last_name="b", email="a.b@toto.fr"
        )
        cls.subscribers = Group.objects.get(name="Subscribers")
        cls.old_subscribers = Group.objects.get(name="Old subscribers")
        cls.accounting_admin = Group.objects.get(name="Accounting admin")
        cls.com_admin = Group.objects.get(name="Communication admin")
        cls.counter_admin = Group.objects.get(name="Counter admin")
        cls.banned_alcohol = Group.objects.get(name="Banned from buying alcohol")
        cls.banned_counters = Group.objects.get(name="Banned from counters")
        cls.banned_subscription = Group.objects.get(name="Banned to subscribe")
        cls.sas_admin = Group.objects.get(name="SAS admin")
        cls.club = Club.objects.create(
            name="Fake Club",
            unix_name="fake-club",
            address="Fake address",
        )
        cls.main_club = Club.objects.get(id=1)

    def assert_in_public_group(self, user):
        assert user.is_in_group(pk=self.public.id)
        assert user.is_in_group(name=self.public.name)

    def assert_in_club_metagroups(self, user, club):
        meta_groups_board = club.unix_name + settings.SITH_BOARD_SUFFIX
        meta_groups_members = club.unix_name + settings.SITH_MEMBER_SUFFIX
        assert user.is_in_group(name=meta_groups_board) is False
        assert user.is_in_group(name=meta_groups_members) is False

    def assert_only_in_public_group(self, user):
        self.assert_in_public_group(user)
        for group in (
            self.root_group,
            self.banned_counters,
            self.accounting_admin,
            self.sas_admin,
            self.subscribers,
            self.old_subscribers,
        ):
            assert not user.is_in_group(pk=group.pk)
            assert not user.is_in_group(name=group.name)
        meta_groups_board = self.club.unix_name + settings.SITH_BOARD_SUFFIX
        meta_groups_members = self.club.unix_name + settings.SITH_MEMBER_SUFFIX
        assert user.is_in_group(name=meta_groups_board) is False
        assert user.is_in_group(name=meta_groups_members) is False

    def test_anonymous_user(self):
        """Test that anonymous users are only in the public group."""
        user = AnonymousUser()
        self.assert_only_in_public_group(user)

    def test_not_subscribed_user(self):
        """Test that users who never subscribed are only in the public group."""
        self.assert_only_in_public_group(self.toto)

    def test_wrong_parameter_fail(self):
        """Test that when neither the pk nor the name argument is given,
        the function raises a ValueError.
        """
        with self.assertRaises(ValueError):
            self.toto.is_in_group()

    def test_number_queries(self):
        """Test that the number of db queries is stable
        and that less queries are made when making a new call.
        """
        # make sure Skia is in at least one group
        self.skia.groups.add(Group.objects.first().pk)
        skia_groups = self.skia.groups.all()

        group_in = skia_groups.first()
        cache.clear()
        # Test when the user is in the group
        with self.assertNumQueries(2):
            self.skia.is_in_group(pk=group_in.id)
        with self.assertNumQueries(0):
            self.skia.is_in_group(pk=group_in.id)

        ids = skia_groups.values_list("pk", flat=True)
        group_not_in = Group.objects.exclude(pk__in=ids).first()
        cache.clear()
        # Test when the user is not in the group
        with self.assertNumQueries(2):
            self.skia.is_in_group(pk=group_not_in.id)
        with self.assertNumQueries(0):
            self.skia.is_in_group(pk=group_not_in.id)

    def test_cache_properly_cleared_membership(self):
        """Test that when the membership of a user end,
        the cache is properly invalidated.
        """
        membership = Membership.objects.create(
            club=self.club, user=self.toto, end_date=None
        )
        meta_groups_members = self.club.unix_name + settings.SITH_MEMBER_SUFFIX
        cache.clear()
        assert self.toto.is_in_group(name=meta_groups_members) is True
        assert membership == cache.get(f"membership_{self.club.id}_{self.toto.id}")
        membership.end_date = now() - timedelta(minutes=5)
        membership.save()
        cached_membership = cache.get(f"membership_{self.club.id}_{self.toto.id}")
        assert cached_membership == "not_member"
        assert self.toto.is_in_group(name=meta_groups_members) is False

    def test_cache_properly_cleared_group(self):
        """Test that when a user is removed from a group,
        the is_in_group_method return False when calling it again.
        """
        # testing with pk
        self.toto.groups.add(self.com_admin.pk)
        assert self.toto.is_in_group(pk=self.com_admin.pk) is True

        self.toto.groups.remove(self.com_admin.pk)
        assert self.toto.is_in_group(pk=self.com_admin.pk) is False

        # testing with name
        self.toto.groups.add(self.sas_admin.pk)
        assert self.toto.is_in_group(name="SAS admin") is True

        self.toto.groups.remove(self.sas_admin.pk)
        assert self.toto.is_in_group(name="SAS admin") is False

    def test_not_existing_group(self):
        """Test that searching for a not existing group
        returns False.
        """
        assert self.skia.is_in_group(name="This doesn't exist") is False


class TestDateUtils(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.autumn_month = settings.SITH_SEMESTER_START_AUTUMN[0]
        cls.autumn_day = settings.SITH_SEMESTER_START_AUTUMN[1]
        cls.spring_month = settings.SITH_SEMESTER_START_SPRING[0]
        cls.spring_day = settings.SITH_SEMESTER_START_SPRING[1]

        cls.autumn_semester_january = date(2025, 1, 4)
        cls.autumn_semester_september = date(2024, 9, 4)
        cls.autumn_first_day = date(2024, cls.autumn_month, cls.autumn_day)

        cls.spring_semester_march = date(2023, 3, 4)
        cls.spring_first_day = date(2023, cls.spring_month, cls.spring_day)

    def test_get_semester(self):
        """Test that the get_semester function returns the correct semester string."""
        assert get_semester_code(self.autumn_semester_january) == "A24"
        assert get_semester_code(self.autumn_semester_september) == "A24"
        assert get_semester_code(self.autumn_first_day) == "A24"

        assert get_semester_code(self.spring_semester_march) == "P23"
        assert get_semester_code(self.spring_first_day) == "P23"

    def test_get_start_of_semester_fixed_date(self):
        """Test that the get_start_of_semester correctly the starting date of the semester."""
        automn_2024 = date(2024, self.autumn_month, self.autumn_day)
        assert get_start_of_semester(self.autumn_semester_january) == automn_2024
        assert get_start_of_semester(self.autumn_semester_september) == automn_2024
        assert get_start_of_semester(self.autumn_first_day) == automn_2024

        spring_2023 = date(2023, self.spring_month, self.spring_day)
        assert get_start_of_semester(self.spring_semester_march) == spring_2023
        assert get_start_of_semester(self.spring_first_day) == spring_2023

    def test_get_start_of_semester_today(self):
        """Test that the get_start_of_semester returns the start of the current semester
        when no date is given.
        """
        with freezegun.freeze_time(self.autumn_semester_september):
            assert get_start_of_semester() == self.autumn_first_day

        with freezegun.freeze_time(self.spring_semester_march):
            assert get_start_of_semester() == self.spring_first_day

    def test_get_start_of_semester_changing_date(self):
        """Test that the get_start_of_semester correctly gives the starting date of the semester,
        even when the semester changes while the server isn't restarted.
        """
        spring_2023 = date(2023, self.spring_month, self.spring_day)
        autumn_2023 = date(2023, self.autumn_month, self.autumn_day)
        mid_spring = spring_2023 + timedelta(days=45)
        mid_autumn = autumn_2023 + timedelta(days=45)

        with freezegun.freeze_time(mid_spring) as frozen_time:
            assert get_start_of_semester() == spring_2023

            # forward time to the middle of the next semester
            frozen_time.move_to(mid_autumn)
            assert get_start_of_semester() == autumn_2023
