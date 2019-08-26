# -*- coding: utf-8 -*-
##############################################################################
#
#   Check Payment
#   Authors: Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#   Company: Basement720 Technology Inc.
#
#   Copyright 2018 Dominador B. Ramos Jr.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
##############################################################################
{
    'name': 'Check Payment',
    'category': 'Accounting',
    'summary': 'Issuing and receving check for payment account',
    'version': '1.0',
    'description': """Check Payment""",
    'author': 'Mong Ramos Jr. <mongramosjr@gmail.com>',
    'website': 'https://www.basement720.com/',
    'depends': ['account_payment'],
    'data': [
        'security/account_check_payment_security.xml',
        'security/ir.model.access.csv',
        'views/account_payment_views.xml',
        'views/check_payment_views.xml',
        'views/check_payment_transaction_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
