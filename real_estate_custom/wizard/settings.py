# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    phone_is_unique = fields.Boolean(string="Phone Is Unique", default=False)
    default_account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                                  default_model='product.template', )
    default_account_income = fields.Many2one('account.account', 'Income Account', default_model='product.template', )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameter = self.env['ir.config_parameter'].sudo()
        config_parameter.set_param('phone.is.unique', self.phone_is_unique)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update({
            'phone_is_unique': self.env['ir.config_parameter'].sudo().get_param('phone.is.unique'),
        })
        return res
