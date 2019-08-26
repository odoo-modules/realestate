# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


#
class accountVoucher(models.Model):

    _inherit = 'account.voucher'

    account_voucher_id = fields.One2many('loan.line.rs.own','rel')




class LoanLineRsOwn(models.Model):

    _inherit = 'loan.line.rs.own'

    phone = fields.Char(string="Phone", required=False, related="contract_partner_id.phone")
    due_amount = fields.Float(string="Due Amount", required=False, )



    # company_id = fields.Many2one('res.company', string='Company', change_default=True, required=True, readonly=True,
    #                              states={'draft': [('readonly', False)]},
    #                              default=lambda self: self.env['res.company'].browse(
    #                                  self.env['res.company']._company_default_get('account.voucher')))

    rel = fields.Many2one(comodel_name='account.voucher',default=lambda self: self.env['res.company']._company_default_get('account.voucher'))
    voucher_num = fields.Char(string="Voucher",related="rel.number",store=True)
    acc_date = fields.Date(related="rel.account_date",store=True)






    # @api.depends('voucher_num')
    # def comp(self):
    #     print(self)



class LoanLineRs(models.Model):
    _inherit = 'loan.line.rs'

    due_amount = fields.Float(string="Due Amount", required=False, )
