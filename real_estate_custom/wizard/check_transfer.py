# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta


class CheckTransfer(models.TransientModel):
    _name = 'check.transfer'
    _rec_name = 'check_name'
    _description = 'Check Transfer'

    check_name = fields.Char('Name', required=True, )
    check_number = fields.Char('Number', required=True)
    check_issue_date = fields.Date('Issue Date', default=fields.Date.context_today)
    check_payment_date = fields.Date('Payment Date', required=True, help="Only if this check is post dated")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    amount = fields.Monetary(string='Amount', required=True)

    bank_id = fields.Many2one('res.bank', string="Bank Name", ondelete='restrict', copy=False)

    payment_id = fields.Many2one(comodel_name="customer.payment.check", string="Customer Payment ", required=False, )
