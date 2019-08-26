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
import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    check_payment_transaction_ids = fields.One2many('check.payment.transaction.payment', 'account_payment_id', string="Check Information",
        readonly=True, states={'draft': [('readonly', False)]}, copy=False)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    hide_check_payment = fields.Boolean(compute='_compute_hide_check_payment',
        help="Technical field used to hide the check_payment if the selected journal has not been set or the selected journal has a type neither in in bank nor cash")

    check_payment_transaction_ids = fields.One2many('check.payment.transaction.payment', 'account_payment_id', string="Check Information",
        readonly=True, states={'draft': [('readonly', False)]}, copy=False)

    @api.multi
    def write(self, vals):
        
        for rec in self:
            if 'journal_id' in vals:
                for check_payment in rec.check_payment_transaction_ids:
                    check_payment.journal_id = vals['journal_id']
            if 'partner_id' in vals:
                for check_payment in rec.check_payment_transaction_ids:
                    check_payment.partner_id = vals['partner_id']
            if 'currency_id' in vals:
                for check_payment in rec.check_payment_transaction_ids:
                    check_payment.currency_id = vals['currency_id']
            if 'payment_type' in vals:
                for check_payment in rec.check_payment_transaction_ids:
                    if vals['payment_type'] == 'inbound':
                        check_payment.payment_type = 'inbound'
                    elif vals['payment_type'] == 'outbound':
                        check_payment.payment_type = 'outbound'
        res = super(AccountPayment, self).write(vals)
        
        return res

    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        for rec in self:
            for check_payment in rec.check_payment_transaction_ids:
                if check_payment.state == 'draft':
                    if rec.payment_type == 'inbound':
                        check_payment.action_receive()
                    if rec.payment_type == 'outbound':
                        check_payment.action_issue()
                    
        
    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        if self.payment_type == 'transfer':
            self.hide_check_payment = True
        elif self.payment_type == 'outbound' or self.payment_type == 'inbound':
            if self.journal_id.type == 'bank' or self.journal_id.type == 'cash':
                self.hide_check_payment = False
            else:
                self.hide_check_payment = True
        #res['domain']['payment_type'] = self.payment_type
        return res
        
    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(AccountPayment, self)._onchange_journal()
        if self.journal_id:
            if self.check_payment_transaction_ids:
                for rec in self.check_payment_transaction_ids:
                    rec.journal_id = self.journal_id
        return res

    @api.multi
    @api.depends('journal_id')
    def _compute_hide_check_payment(self):
        for payment in self:
            if payment.payment_type == 'transfer':
                payment.hide_check_payment = True
                continue
            if not payment.journal_id:
                payment.hide_check_payment = True
                continue
            if payment.payment_type == 'outbound' or payment.payment_type == 'inbound':
                if payment.journal_id.type == 'bank' or payment.journal_id.type == 'cash':
                    payment.hide_check_payment = False
                else:
                    payment.hide_check_payment = True
