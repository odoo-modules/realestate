# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta


class UnitRefund(models.TransientModel):
    _inherit = 'customer.payment.refund'

    def refund(self):
        res = super(UnitRefund, self).refund()
        contract = self.contract
        contract.building_unit.write({'state': 'free'})
        return res
