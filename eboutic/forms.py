# -*- coding:utf-8 -*
#
# Copyright 2022
# - Maréchal <thgirod@hotmail.com
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
# this program; if not, write to the Free Sofware Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA 02111-1307, USA.
#
#

import json
import re

from django.http import HttpRequest
from django.utils.translation import gettext as _

from counter.models import Counter
from sith import settings


class BasketForm:
    """
    Class intended to perform checks on the request sended to the server when
    the user submits his basket from /eboutic/

    Because it must check an unknown number of fields, coming from a cookie
    and needing some databases checks to be performed, inheriting from forms.Form
    or using formset would have been likely to end in a big ball of wibbly-wobbly hacky stuff.
    Thus this class is a pure standalone and performs its operations by its own means.
    However, it still tries to share some similarities with a standard django Form.

    Usage example: ::

        def my_view(request):
            form = BasketForm(request)
            form.clean()
            if form.is_valid():
                # perform operations
            else:
                errors = form.get_error_messages()

                # return the cookie that was in the request, but with all
                # incorrects elements removed
                cookie = form.get_cleaned_cookie()

    You can also use a little shortcut by directly calling `form.is_valid()`
    without calling `form.clean()`. In this case, the latter method shall be
    implicitly called.
    """

    json_cookie_re = re.compile(
        r"^\[\s*(\{\s*(\"[^\"]*\":\s*(\"[^\"]{0,64}\"|\d{0,5}\.?\d+),?\s*)*\},?\s*)*\s*\]$"
    )

    def __init__(self, request: HttpRequest):
        self.user = request.user
        self.cookies = request.COOKIES
        self.error_messages = set()
        self.correct_cookie = []

    def clean(self):
        """
        Perform all the check, but return nothing.
        To know if the form is valid, the `is_valid()` method must be used.

        The form shall be considered as valid if it meets all the following conditions :
            - it contains a "basket_items" key in the cookies of the request given in the constructor
            - this cookie is a list of objects formatted this way : `[{'id': <int>, 'quantity': <int>,
             'name': <str>, 'unit_price': <float>}, ...]`. The order of the fields in each object does not matter
            - all the ids are positive integers
            - all the ids refer to products available in the EBOUTIC
            - all the ids refer to products the user is allowed to buy
            - all the quantities are positive integers
        """
        basket = self.cookies.get("basket_items", None)
        print(basket)
        if basket is None or basket in ("[]", ""):
            self.error_messages.add("You have no basket")
            return
        # check that the json is not nested before parsing it to make sure
        # malicious user can't ddos the server with deeply nested json
        if not BasketForm.json_cookie_re.match(basket):
            self.error_messages.add("The request was badly formatted.")
            return
        try:
            basket = json.loads(basket)
        except json.JSONDecodeError:
            self.error_messages.add("The request was badly formatted.")
            return
        if type(basket) is not list or len(basket) == 0:
            self.error_messages.add("The request was badly formatted.")
            return
        eboutique = Counter.objects.get(type="EBOUTIC")
        user_is_subscribed = self.user.subscriptions.exists()
        for item in basket:
            expected_keys = {"id", "quantity", "name", "unit_price"}
            if type(item) is not dict or set(item.keys()) != expected_keys:
                self.error_messages.add("One or more items are badly formatted.")
                continue
            if type(item["id"]) is not int or item["id"] < 0:
                self.error_messages.add("One or more item do not exist.")
                continue
            product = eboutique.products.filter(id=(item["id"]))
            if not product.exists():
                self.error_messages.add("One or more item do not exist.")
                continue
            if not product.first().can_be_sold_to(self.user):
                self.error_messages.add("You are not allowed to buy one or more items.")
                continue
            if type(item["quantity"]) is not int or item["quantity"] < 0:
                self.error_messages.add(
                    "You have requested an invalid quantity of one or more items."
                )
                continue
            subscription = settings.SITH_PRODUCTTYPE_SUBSCRIPTION
            if (
                product.first().product_type_id == subscription
                and not user_is_subscribed
            ):
                self.error_messages.add(
                    "You cannot buy a subscription if you have not "
                    "been a subscriber at least once before."
                )
                continue

            # if we arrive here, it means this item has passed all tests
            self.correct_cookie.append(item)
            # for loop for item checking ends here

    def is_valid(self) -> True:
        """
        return True if the form is correct else False.
        If the `clean()` method has not been called beforehand, call it
        """
        if self.error_messages == set() and self.correct_cookie == []:
            self.clean()
        if self.error_messages:
            return False
        return True

    def get_error_messages(self):
        return [_(msg) for msg in self.error_messages]

    def get_cleaned_cookie(self):
        if not self.correct_cookie:
            return ""
        return json.dumps(self.correct_cookie)
