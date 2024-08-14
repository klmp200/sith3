#
# Copyright 2016,2017,2024
# - Skia <skia@libskia.so>
# - Sli <antoine@bartuccio.fr>
#
# Ce fichier fait partie du site de l'Association des Étudiants de l'UTBM,
# http://ae.utbm.fr.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License a published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA 02111-1307, USA.
#
#

"""Django settings for sith project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

import binascii
import logging
import os
import sys
from pathlib import Path

import sentry_sdk
from django.utils.translation import gettext_lazy as _
from sentry_sdk.integrations.django import DjangoIntegration

from .honeypot import custom_honeypot_error

BASE_DIR = Path(__file__).parent.parent.resolve()

os.environ["HTTPS"] = "off"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "(4sjxvhz@m5$0a$j0_pqicnc$s!vbve)z+&++m%g%bjhlz4+g2"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TESTING = "pytest" in sys.modules
INTERNAL_IPS = ["127.0.0.1"]

ALLOWED_HOSTS = ["*"]

# Application definition

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

SITE_ID = 4000

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "honeypot",
    "django_jinja",
    "ninja_extra",
    "ajax_select",
    "haystack",
    "captcha",
    "core",
    "club",
    "subscription",
    "accounting",
    "counter",
    "eboutic",
    "launderette",
    "rootplace",
    "sas",
    "com",
    "election",
    "forum",
    "stock",
    "trombi",
    "matmat",
    "pedagogy",
    "galaxy",
    "antispam",
)

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "core.middleware.AuthenticationMiddleware",
    "core.middleware.SignalRequestMiddleware",
)

ROOT_URLCONF = "sith.urls"

TEMPLATES = [
    {
        "NAME": "jinja2",
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "match_extension": ".jinja",
            "app_dirname": "templates",
            "newstyle_gettext": True,
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
            "extensions": [
                "jinja2.ext.do",
                "jinja2.ext.loopcontrols",
                "jinja2.ext.i18n",
                "django_jinja.builtins.extensions.CsrfExtension",
                "django_jinja.builtins.extensions.CacheExtension",
                "django_jinja.builtins.extensions.TimezoneExtension",
                "django_jinja.builtins.extensions.UrlsExtension",
                "django_jinja.builtins.extensions.StaticFilesExtension",
                "django_jinja.builtins.extensions.DjangoFiltersExtension",
                "core.templatetags.extensions.HoneypotExtension",
            ],
            "filters": {
                "markdown": "core.templatetags.renderer.markdown",
                "phonenumber": "core.templatetags.renderer.phonenumber",
                "truncate_time": "core.templatetags.renderer.truncate_time",
                "format_timedelta": "core.templatetags.renderer.format_timedelta",
            },
            "globals": {
                "can_edit_prop": "core.views.can_edit_prop",
                "can_edit": "core.views.can_edit",
                "can_view": "core.views.can_view",
                "settings": "sith.settings",
                "Launderette": "launderette.models.Launderette",
                "Counter": "counter.models.Counter",
                "ProductType": "counter.models.ProductType",
                "timezone": "django.utils.timezone",
                "get_sith": "com.views.sith",
                "scss": "core.templatetags.renderer.scss",
            },
            "bytecode_cache": {
                "name": "default",
                "backend": "django_jinja.cache.BytecodeCache",
                "enabled": False,
            },
            "autoescape": True,
            "auto_reload": True,
            "translation_engine": "django.utils.translation",
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    },
]
FORM_RENDERER = "django.forms.renderers.DjangoDivFormRenderer"

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "xapian_backend.XapianEngine",
        "PATH": os.path.join(os.path.dirname(__file__), "search_indexes", "xapian"),
        "INCLUDE_SPELLING": True,
    }
}

HAYSTACK_SIGNAL_PROCESSOR = "core.search_indexes.IndexSignalProcessor"

SASS_PRECISION = 8

WSGI_APPLICATION = "sith.wsgi.application"

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "log_to_stdout": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "main": {
            "handlers": ["log_to_stdout"],
            "level": "INFO",
            "propagate": True,
        }
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = "fr-FR"

LANGUAGES = [("en", _("English")), ("fr", _("French"))]

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]

PHONENUMBER_DEFAULT_REGION = "FR"

# Medias
MEDIA_URL = "/data/"
MEDIA_ROOT = BASE_DIR / "data"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

# Static files finders which allow to see static folder in all apps
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "sith.finders.ScssFinder",
]

# Auth configuration
AUTH_USER_MODEL = "core.User"
AUTH_ANONYMOUS_MODEL = "core.models.AnonymousUser"
LOGIN_URL = "/login"
LOGOUT_URL = "/logout"
LOGIN_REDIRECT_URL = "/"
DEFAULT_FROM_EMAIL = "bibou@git.an"
SITH_COM_EMAIL = "bibou_com@git.an"

# Those values are to be changed in production to be more effective
HONEYPOT_FIELD_NAME = "body2"
HONEYPOT_VALUE = "content"
HONEYPOT_RESPONDER = custom_honeypot_error  # Make honeypot errors less suspicious
HONEYPOT_FIELD_NAME_FORUM = "message2"  # Only used on forum

# Email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 25

# Below this line, only Sith-specific variables are defined

SITH_URL = "my.url.git.an"
SITH_NAME = "Sith website"
SITH_TWITTER = "@ae_utbm"

# Enable experimental features
# Enable/Disable the galaxy button on user profile (urls stay activated)
SITH_ENABLE_GALAXY = False

# AE configuration
# TODO: keep only that first setting, with the ID, and do the same for the other clubs
SITH_MAIN_CLUB_ID = 1
SITH_MAIN_CLUB = {
    "name": "AE",
    "unix_name": "ae",
    "address": "6 Boulevard Anatole France, 90000 Belfort",
}

# Bar managers
SITH_BAR_MANAGER = {
    "name": "Pdf",
    "unix_name": "pdfesti",
    "address": "6 Boulevard Anatole France, 90000 Belfort",
}

# Launderette managers
SITH_LAUNDERETTE_MANAGER = {
    "name": "Laverie",
    "unix_name": "laverie",
    "address": "6 Boulevard Anatole France, 90000 Belfort",
}

# Main root for club pages
SITH_CLUB_ROOT_PAGE = "clubs"

# Define the date in the year serving as reference for the subscriptions calendar
# (month, day)
SITH_SEMESTER_START_AUTUMN = (8, 15)  # 15 August
SITH_SEMESTER_START_SPRING = (2, 15)  # 15 February

# Used to determine the valid promos
SITH_SCHOOL_START_YEAR = 1999

SITH_GROUP_ROOT_ID = 1
SITH_GROUP_PUBLIC_ID = 2
SITH_GROUP_SUBSCRIBERS_ID = 3
SITH_GROUP_OLD_SUBSCRIBERS_ID = 4
SITH_GROUP_ACCOUNTING_ADMIN_ID = 5
SITH_GROUP_COM_ADMIN_ID = 6
SITH_GROUP_COUNTER_ADMIN_ID = 7
SITH_GROUP_BANNED_ALCOHOL_ID = 8
SITH_GROUP_BANNED_COUNTER_ID = 9
SITH_GROUP_BANNED_SUBSCRIPTION_ID = 10
SITH_GROUP_SAS_ADMIN_ID = 11
SITH_GROUP_FORUM_ADMIN_ID = 12
SITH_GROUP_PEDAGOGY_ADMIN_ID = 13

SITH_CLUB_REFOUND_ID = 89
SITH_COUNTER_REFOUND_ID = 38
SITH_PRODUCT_REFOUND_ID = 5

# Pages
SITH_CORE_PAGE_SYNTAX = "Aide_sur_la_syntaxe"

# Forum

SITH_FORUM_PAGE_LENGTH = 30

# SAS variables
SITH_SAS_ROOT_DIR_ID = 4
SITH_SAS_IMAGES_PER_PAGE = 60

SITH_BOARD_SUFFIX = "-bureau"
SITH_MEMBER_SUFFIX = "-membres"

SITH_MAIN_BOARD_GROUP = SITH_MAIN_CLUB["unix_name"] + SITH_BOARD_SUFFIX
SITH_MAIN_MEMBERS_GROUP = SITH_MAIN_CLUB["unix_name"] + SITH_MEMBER_SUFFIX
SITH_BAR_MANAGER_BOARD_GROUP = SITH_BAR_MANAGER["unix_name"] + SITH_BOARD_SUFFIX

SITH_PROFILE_DEPARTMENTS = [
    ("TC", _("TC")),
    ("IMSI", _("IMSI")),
    ("IMAP", _("IMAP")),
    ("INFO", _("INFO")),
    ("GI", _("GI")),
    ("E", _("E")),
    ("EE", _("EE")),
    ("GESC", _("GESC")),
    ("GMC", _("GMC")),
    ("MC", _("MC")),
    ("EDIM", _("EDIM")),
    ("HUMA", _("Humanities")),
    ("NA", _("N/A")),
]

SITH_ACCOUNTING_PAYMENT_METHOD = [
    ("CHECK", _("Check")),
    ("CASH", _("Cash")),
    ("TRANSFERT", _("Transfert")),
    ("CARD", _("Credit card")),
]

SITH_SUBSCRIPTION_PAYMENT_METHOD = [
    ("CHECK", _("Check")),
    ("CARD", _("Credit card")),
    ("CASH", _("Cash")),
    ("EBOUTIC", _("Eboutic")),
    ("OTHER", _("Other")),
]

SITH_SUBSCRIPTION_LOCATIONS = [
    ("BELFORT", _("Belfort")),
    ("SEVENANS", _("Sevenans")),
    ("MONTBELIARD", _("Montbéliard")),
    ("EBOUTIC", _("Eboutic")),
]

SITH_COUNTER_BARS = [(1, "MDE"), (2, "Foyer"), (35, "La Gommette")]

SITH_COUNTER_OFFICES = {2: "PdF", 1: "AE"}

SITH_COUNTER_PAYMENT_METHOD = [
    ("CHECK", _("Check")),
    ("CASH", _("Cash")),
    ("CARD", _("Credit card")),
]

SITH_COUNTER_BANK = [
    ("OTHER", "Autre"),
    ("SOCIETE-GENERALE", "Société générale"),
    ("BANQUE-POPULAIRE", "Banque populaire"),
    ("BNP", "BNP"),
    ("CAISSE-EPARGNE", "Caisse d'épargne"),
    ("CIC", "CIC"),
    ("CREDIT-AGRICOLE", "Crédit Agricole"),
    ("CREDIT-MUTUEL", "Credit Mutuel"),
    ("CREDIT-LYONNAIS", "Credit Lyonnais"),
    ("LA-POSTE", "La Poste"),
]

SITH_PEDAGOGY_UV_TYPE = [
    ("FREE", _("Free")),
    ("CS", _("CS")),
    ("TM", _("TM")),
    ("OM", _("OM")),
    ("QC", _("QC")),
    ("EC", _("EC")),
    ("RN", _("RN")),
    ("ST", _("ST")),
    ("EXT", _("EXT")),
]

SITH_PEDAGOGY_UV_SEMESTER = [
    ("CLOSED", _("Closed")),
    ("AUTUMN", _("Autumn")),
    ("SPRING", _("Spring")),
    ("AUTUMN_AND_SPRING", _("Autumn and spring")),
]

SITH_PEDAGOGY_UV_LANGUAGE = [
    ("FR", _("French")),
    ("EN", _("English")),
    ("DE", _("German")),
    ("SP", _("Spanish")),
]

SITH_PEDAGOGY_UV_RESULT_GRADE = [
    ("A", _("A")),
    ("B", _("B")),
    ("C", _("C")),
    ("D", _("D")),
    ("E", _("E")),
    ("FX", _("FX")),
    ("F", _("F")),
    ("ABS", _("Abs")),
]

SITH_LOG_OPERATION_TYPE = [
    ("SELLING_DELETION", _("Selling deletion")),
    ("REFILLING_DELETION", _("Refilling deletion")),
]

SITH_PEDAGOGY_UTBM_API = "https://extranet1.utbm.fr/gpedago/api/guide"

SITH_ECOCUP_CONS = 1152

SITH_ECOCUP_DECO = 1151

# The limit is the maximum difference between cons and deco possible for a customer
SITH_ECOCUP_LIMIT = 3

# Defines pagination for cash summary
SITH_COUNTER_CASH_SUMMARY_LENGTH = 50

# Defines which product type is the refilling type, and thus increases the account amount
SITH_COUNTER_PRODUCTTYPE_REFILLING = 3

# Defines which product is the one year subscription and which one is the six month subscription
SITH_PRODUCT_SUBSCRIPTION_ONE_SEMESTER = 1
SITH_PRODUCT_SUBSCRIPTION_TWO_SEMESTERS = 2
SITH_PRODUCTTYPE_SUBSCRIPTION = 2

# Defines which club lets its member the ability to make subscriptions
# Elements of this list are club's id
SITH_CAN_CREATE_SUBSCRIPTIONS = [1]

# Defines which clubs lets its members the ability to see users subscription history
# Elements of this list are club's id
SITH_CAN_READ_SUBSCRIPTION_HISTORY = []

# Number of weeks before the end of a subscription when the subscriber can resubscribe
SITH_SUBSCRIPTION_END = 10

# Subscription durations are in semestres
# Be careful, modifying this parameter will need a migration to be applied
SITH_SUBSCRIPTIONS = {
    "un-semestre": {"name": _("One semester"), "price": 20, "duration": 1},
    "deux-semestres": {"name": _("Two semesters"), "price": 35, "duration": 2},
    "cursus-tronc-commun": {
        "name": _("Common core cursus"),
        "price": 60,
        "duration": 4,
    },
    "cursus-branche": {"name": _("Branch cursus"), "price": 60, "duration": 6},
    "cursus-alternant": {"name": _("Alternating cursus"), "price": 30, "duration": 6},
    "membre-honoraire": {"name": _("Honorary member"), "price": 0, "duration": 666},
    "assidu": {"name": _("Assidu member"), "price": 0, "duration": 2},
    "amicale/doceo": {"name": _("Amicale/DOCEO member"), "price": 0, "duration": 2},
    "reseau-ut": {"name": _("UT network member"), "price": 0, "duration": 1},
    "crous": {"name": _("CROUS member"), "price": 0, "duration": 2},
    "sbarro/esta": {"name": _("Sbarro/ESTA member"), "price": 15, "duration": 2},
    "un-semestre-welcome": {
        "name": _("One semester Welcome Week"),
        "price": 0,
        "duration": 1,
    },
    "un-mois-essai": {"name": _("One month for free"), "price": 0, "duration": 0.166},
    "deux-mois-essai": {"name": _("Two months for free"), "price": 0, "duration": 0.33},
    "benevoles-euroks": {"name": _("Eurok's volunteer"), "price": 5, "duration": 0.1},
    "six-semaines-essai": {
        "name": _("Six weeks for free"),
        "price": 0,
        "duration": 0.23,
    },
    "un-jour": {"name": _("One day"), "price": 0, "duration": 0.00555333},
    "membre-staff-ga": {"name": _("GA staff member"), "price": 1, "duration": 0.076},
    # Discount subscriptions
    "un-semestre-reduction": {
        "name": _("One semester (-20%)"),
        "price": 12,
        "duration": 1,
    },
    "deux-semestres-reduction": {
        "name": _("Two semesters (-20%)"),
        "price": 22,
        "duration": 2,
    },
    "cursus-tronc-commun-reduction": {
        "name": _("Common core cursus (-20%)"),
        "price": 36,
        "duration": 4,
    },
    "cursus-branche-reduction": {
        "name": _("Branch cursus (-20%)"),
        "price": 36,
        "duration": 6,
    },
    "cursus-alternant-reduction": {
        "name": _("Alternating cursus (-20%)"),
        "price": 24,
        "duration": 6,
    },
    # CA special offer
    "un-an-offert-CA": {
        "name": _("One year for free(CA offer)"),
        "price": 0,
        "duration": 2,
    },
    # To be completed....
}

SITH_CLUB_ROLES_ID = {
    "President": 10,
    "Vice-President": 9,
    "Treasurer": 7,
    "Communication supervisor": 5,
    "Secretary": 4,
    "IT supervisor": 3,
    "Board member": 2,
    "Active member": 1,
    "Curious": 0,
}

SITH_CLUB_ROLES = {
    10: _("President"),
    9: _("Vice-President"),
    7: _("Treasurer"),
    5: _("Communication supervisor"),
    4: _("Secretary"),
    3: _("IT supervisor"),
    2: _("Board member"),
    1: _("Active member"),
    0: _("Curious"),
}

# This corresponds to the maximum role a user can freely subscribe to
# In this case, SITH_MAXIMUM_FREE_ROLE=1 means that a user can
# set himself as "Membre actif" or "Curieux", but not higher
SITH_MAXIMUM_FREE_ROLE = 1

# Minutes to timeout the logged barmen
SITH_BARMAN_TIMEOUT = 20

# Minutes to delete the last operations
SITH_LAST_OPERATIONS_LIMIT = 10

# Minutes for a counter to be inactive
SITH_COUNTER_MINUTE_INACTIVE = 10

# ET variables
SITH_EBOUTIC_CB_ENABLED = True
SITH_EBOUTIC_ET_URL = (
    "https://preprod-tpeweb.e-transactions.fr/cgi/MYchoix_pagepaiement.cgi"
)
SITH_EBOUTIC_PBX_SITE = "1999888"
SITH_EBOUTIC_PBX_RANG = "32"
SITH_EBOUTIC_PBX_IDENTIFIANT = "2"
SITH_EBOUTIC_HMAC_KEY = binascii.unhexlify(
    "0123456789ABCDEF0123456789ABCDEF"
    "0123456789ABCDEF0123456789ABCDEF"
    "0123456789ABCDEF0123456789ABCDEF"
    "0123456789ABCDEF0123456789ABCDEF"
)
SITH_EBOUTIC_PUB_KEY = ""
with open(os.path.join(os.path.dirname(__file__), "et_keys/pubkey.pem")) as f:
    SITH_EBOUTIC_PUB_KEY = f.read()

# Launderette variables
SITH_LAUNDERETTE_MACHINE_TYPES = [("WASHING", _("Washing")), ("DRYING", _("Drying"))]
SITH_LAUNDERETTE_PRICES = {"WASHING": 1.0, "DRYING": 0.75}

SITH_NOTIFICATIONS = [
    ("POSTER_MODERATION", _("A new poster needs to be moderated")),
    ("MAILING_MODERATION", _("A new mailing list needs to be moderated")),
    (
        "PEDAGOGY_MODERATION",
        _("A new pedagogy comment has been signaled for moderation"),
    ),
    ("NEWS_MODERATION", _("There are %s fresh news to be moderated")),
    ("FILE_MODERATION", _("New files to be moderated")),
    ("SAS_MODERATION", _("There are %s pictures to be moderated in the SAS")),
    ("NEW_PICTURES", _("You've been identified on some pictures")),
    ("REFILLING", _("You just refilled of %s €")),
    ("SELLING", _("You just bought %s")),
    ("GENERIC", _("You have a notification")),
]

# The keys are the notification names as found in SITH_NOTIFICATIONS, and the
# values are the callback function to update the notifs.
# The callback must take the notif object as first and single argument.
SITH_PERMANENT_NOTIFICATIONS = {
    "NEWS_MODERATION": "com.models.news_notification_callback",
    "SAS_MODERATION": "sas.models.sas_notification_callback",
}

SITH_QUICK_NOTIF = {
    "qn_success": _("Success!"),
    "qn_fail": _("Fail!"),
    "qn_weekmail_new_article": _("You successfully posted an article in the Weekmail"),
    "qn_weekmail_article_edit": _("You successfully edited an article in the Weekmail"),
    "qn_weekmail_send_success": _("You successfully sent the Weekmail"),
}

# Mailing related settings

SITH_MAILING_DOMAIN = "utbm.fr"
SITH_MAILING_FETCH_KEY = "IloveMails"

SITH_GIFT_LIST = [("AE Tee-shirt", _("AE tee-shirt"))]

SENTRY_DSN = ""
SENTRY_ENV = "production"

TOXIC_DOMAINS_PROVIDERS = [
    "https://www.stopforumspam.com/downloads/toxic_domains_whole.txt",
]

try:
    from .settings_custom import *

    logging.getLogger("django").info("Custom settings imported")
except:
    logging.getLogger("django").warning("Custom settings failed")

if DEBUG:
    INSTALLED_APPS += ("debug_toolbar",)
    MIDDLEWARE = ("debug_toolbar.middleware.DebugToolbarMiddleware",) + MIDDLEWARE
    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "sith.toolbar_debug.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]
    SENTRY_ENV = "development"

if TESTING:
    CAPTCHA_TEST_MODE = True
    PASSWORD_HASHERS = [  # not secure, but faster password hasher
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
    STORAGES = {  # store files in memory rather than using the hard drive
        "default": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

if SENTRY_DSN:
    # Connection to sentry
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
        environment=SENTRY_ENV,
    )

SITH_FRONT_DEP_VERSIONS = {
    "https://github.com/gildas-lormeau/zip.js": "2.7.47",
    "https://github.com/jimmywarting/native-file-system-adapter": "3.0.1",
    "https://github.com/chartjs/Chart.js/": "2.6.0",
    "https://github.com/Ionaru/easy-markdown-editor/": "2.18.0",
    "https://github.com/FortAwesome/Font-Awesome/": "4.7.0",
    "https://github.com/jquery/jquery/": "3.6.2",
    "https://github.com/sethmcl/jquery-ui/": "1.11.1",
    "https://github.com/viralpatel/jquery.shorten/": "",
    "https://github.com/getsentry/sentry-javascript/": "8.26.0",
    "https://github.com/jhuckaby/webcamjs/": "1.0.0",
    "https://github.com/alpinejs/alpine": "3.14.1",
    "https://github.com/mrdoob/three.js/": "r148",
    "https://github.com/vasturiano/three-spritetext": "1.6.5",
    "https://github.com/vasturiano/3d-force-graph/": "1.70.19",
    "https://github.com/vasturiano/d3-force-3d": "3.0.3",
}
