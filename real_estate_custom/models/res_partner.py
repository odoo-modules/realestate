# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(required=True, default='01')
    customer_id = fields.Char(string="Customer ID", required=False, )

    @api.model
    def create(self, vals):
        phone_is_unique = self.get_phone_config()
        if phone_is_unique:
            res = self.sudo().search([('phone', '=', vals.get('phone'))])
            if res:
                raise exceptions.ValidationError('Phone Number Is Unique !')
        new_record = super(ResPartner, self).create(vals)
        return new_record

    def get_phone_config(self):
        config_parameter = self.env['ir.config_parameter'].sudo()
        phone_is_unique = config_parameter.get_param('phone.is.unique')
        return phone_is_unique
