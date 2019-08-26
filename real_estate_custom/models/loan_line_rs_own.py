# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class LoanLineRsOwn(models.Model):
    _inherit = 'loan.line.rs.own'

    phone = fields.Char(string="Phone", required=False, related="contract_partner_id.phone")
    due_amount = fields.Float(string="Due Amount", required=False, )


class LoanLineRs(models.Model):
    _inherit = 'loan.line.rs'

    due_amount = fields.Float(string="Due Amount", required=False, )
