# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta
from odoo.tools import float_compare


class ReservationRefund(models.TransientModel):
    _name = 'reservation.refund'
    _description = 'Reservation Refund Wizard'

    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True,
                                 domain=[('type', '=', 'purchase')])
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    refund_amount = fields.Monetary(string="Refund Amount", required=True, )

    def action_refund(self):
        if float_compare(self.refund_amount, 0.0, precision_rounding=0.001) == 0:
            raise exceptions.ValidationError('Refund Amount Must Be Greater Than Zero !')
        elif float_compare(self.refund_amount, 0.0, precision_rounding=0.001) > 0:
            reservation_id = self.env['unit.reservation'].browse(self.env.context.get('active_id'))
            journal_id = self.journal_id
            voucher_obj = self.env['account.voucher']
            voucher_id = voucher_obj.create({'partner_id': reservation_id.partner_id.id,
                                             'real_estate_ref': reservation_id.name,
                                             'name': reservation_id.name,
                                             'account_id': journal_id.default_debit_account_id.id,
                                             'pay_now': 'pay_now',
                                             'reference': reservation_id.name,
                                             'voucher_type': 'purchase',
                                             'journal_id': journal_id.id,
                                             })
            voucher_line_obj = self.env['account.voucher.line']
            voucher_line_obj.create(
                {
                    'voucher_id': voucher_id.id,
                    'name': "Refund Reservation Payment",
                    'price_unit': self.refund_amount,
                    'account_id': reservation_id.partner_id.property_account_receivable_id.id,
                    'account_analytic_id': reservation_id.account_analytic_id.id,
                })

            reservation_id.write({
                'refund_voucher_id': voucher_id.id,
                'is_refunded': True,
            })
