# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class loan_line_rs_wizard(models.TransientModel):
    _inherit = 'loan.line.rs.wizard'

    installment_line_id = fields.Many2one(comodel_name="loan.line.rs.own", string="Installment ID", required=False, )
    due_amount = fields.Float('Due Amount', digits=(16, 4), )
    input_amount = fields.Float('Input Amount', digits=(16, 4), )

    @api.onchange('to_be_paid')
    def onchange_paid(self):
        if self.to_be_paid:
            self.input_amount = self.due_amount
        else:
            self.input_amount = 0.0

    @api.model
    def create(self, vals):
        inst_id = self.env['loan.line.rs.own'].browse(vals.get('installment_line_id'))
        vals['amount'] = inst_id.amount
        vals['due_amount'] = inst_id.due_amount
        vals['date'] = inst_id.date
        new_record = super(loan_line_rs_wizard, self).create(vals)
        return new_record



