# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from datetime import datetime
from dateutil import relativedelta
import time


class create_moves(models.Model):
    _name = 'create.rent.moves'

    @api.multi
    def create_move_lines(self, **kwargs):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        company_currency = self.env.user.company_id.currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=datetime.today()).compute_amount_fields(kwargs['amount'], kwargs['src_currency'], company_currency,
                                                         False)

        move_vals = {
            'name': kwargs['move']['name'],
            'journal_id': kwargs['move']['journal_id'],
            'date': datetime.today(),
            'ref': kwargs['move']['ref'],
            'company_id': kwargs['move']['company_id'],

        }
        move = self.env['account.move'].with_context(check_move_validity=False).create(move_vals)
        debit_line_vals = {
            'name': kwargs['move_line']['name'],
            'account_id': kwargs['debit_account'],
            'analytic_account_id': kwargs['analytic_account'],
            'debit': kwargs['amount'],
            'credit': credit,
            'amount_currency': amount_currency,
            'currency_id': currency_id,
            'partner_id': kwargs['move_line']['partner_id'],
        }

        debit_line_vals['move_id'] = move.id
        aml_obj.create(debit_line_vals)

        credit_line_vals = {
            'name': kwargs['move_line']['name'],
            'account_id': kwargs['credit_account'],
            'analytic_account_id': kwargs['analytic_account'],
            'debit': credit,
            'credit': kwargs['amount'],
            'amount_currency': -1 * amount_currency,
            'currency_id': currency_id,
            'partner_id': kwargs['move_line']['partner_id'], }
        credit_line_vals['move_id'] = move.id
        aml_obj.create(credit_line_vals)
        move.post()
        return True
