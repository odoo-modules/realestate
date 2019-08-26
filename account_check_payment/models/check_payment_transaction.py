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

class CheckPaymentTransactionAbstract(models.AbstractModel):
    _name = "check.payment.transaction.abstract"
    _description = "Contains the logic shared between models which allows to register check payments"


    partner_id = fields.Many2one('res.partner', string='Partner')

    amount = fields.Monetary(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    posted_date = fields.Date(string='Payment Date', required=False, copy=False)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)

    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if self.amount < 0:
            raise ValidationError(_('The payment amount cannot be negative.'))

class CheckPaymentTransaction(models.Model):

    _name = 'check.payment.transaction'
    # inherit = 'check.payment.transaction.abstract' # doesnt include abstract model
    _inherit = ['mail.thread', 'check.payment.transaction.abstract']
    _description = 'Check Payment Transaction'
    _order = 'check_payment_date desc, check_name desc'

    state = fields.Selection([ ('draft', 'Draft'),

        ('received', 'Received'), ('deposited', 'Deposited'),

        ('issued', 'Issued'),

        ('returned', 'Returned'), ('posted', 'Posted'), ('cancelled', 'Cancelled')
    ],
        required=True,
        default='draft',
        copy=False,
        string="Status"
    )

    name = fields.Char(readonly=True, copy=False, default="Draft Check Payment");
    check_name = fields.Char('Name', readonly=True, required=True, copy=True, states={'draft': [('readonly', False)]},)
    check_number = fields.Char('Number', readonly=True, size=34, required=True, copy=True, states={'draft': [('readonly', False)]})
    check_issue_date = fields.Date('Issue Date', readonly=True, copy=False, states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    check_payment_date = fields.Date('Payment Date', readonly=True, required=True, copy=True, help="Only if this check is post dated", states={'draft': [('readonly', False)]})

    amount = fields.Monetary(string='Amount', readonly=True, required=True, states={'draft': [('readonly', False)]})

    bank_id = fields.Many2one('res.bank', string="Bank Name", ondelete='restrict', copy=False)


    payment_type = fields.Selection(compute='_compute_payment_type',
        selection= [('outbound', 'Send Money'), ('inbound', 'Receive Money')], readonly=True, store=True, states={'draft': [('readonly', False)]})

#    @api.model
#    def default_get(self, fields):
#        rec = super(CheckPaymentTransaction, self).default_get(fields)

#        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
#        if invoice_defaults and len(invoice_defaults) == 1:
#            invoice = invoice_defaults[0]
#            rec['currency_id'] = invoice['currency_id'][0]
#            rec['partner_id'] = invoice['partner_id'][0]
#            rec['journal_id'] = invoice['partner_id'][0]
#            rec['amount'] = invoice['residual']
#        return rec

    @api.multi
    def _compute_payment_type(self):
        for rec in self:
            rec.payment_type = 'inbound'
            
    @api.multi
    def unlink(self):
        if any(rec.state != 'draft' for rec in self):
            raise UserError(_("You can not delete a check payment that is already posted"))
        return super(CheckPaymentTransaction, self).unlink()

    @api.multi
    def action_receive(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a check with status draft can be received."))

            rec.name = rec.check_name + ' ' + rec.check_number
            rec.write({'state': 'received'})


    @api.multi
    def action_deposit(self):
        for rec in self:
            if rec.state != 'received':
                raise UserError(_("Only a validated check can be deposited."))


            rec.write({'state': 'deposited'})

    @api.multi
    def action_fund_credited(self):
        for rec in self:
            if rec.state != 'deposited':
                raise UserError(_("Only a check already deposited to bank can be posted."))


            rec.write({'state': 'posted'})


    @api.multi
    def action_return_received_check(self):
        for rec in self:
            if rec.state != 'deposited':
                raise UserError(_("Only a check already deposited to bank can be returned."))


            rec.write({'state': 'returned'})

    @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("You cannot cancel check at this time."))


            rec.write({'state': 'cancelled'})



    @api.multi
    def action_issue(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a check with status draft can be issued."))

            rec.name = rec.check_name + ' ' + rec.check_number
            rec.write({'state': 'issued'})

    @api.multi
    def action_fund_debited(self):
        for rec in self:
            if rec.state != 'issued':
                raise UserError(_("Only a issued check can be posted."))

            rec.write({'state': 'posted'})


    @api.multi
    def action_return_issued_check(self):
        for rec in self:
            if rec.state != 'issued':
                raise UserError(_("Only a issued check can be returned."))

            rec.write({'state': 'returned'})


