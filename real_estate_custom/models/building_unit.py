# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class BuildingUnit(models.Model):
    # _name = "product.template"
    _inherit = ['product.template']
    _description = "Property"

    @api.multi
    def write(self, vals):
        res = super(BuildingUnit, self).write(vals)
        return res

    account_income = fields.Many2one('account.account', 'Income Account')
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    building_area = fields.Float('Building Unit Area m²', )
    price_per_meter = fields.Monetary('Price Per Meter', )
    pricing = fields.Monetary(string="Price", required=False, compute="calc_unit_price", store=True)


    @api.depends('building_area', 'price_per_meter')
    def calc_unit_price(self):
        for unit in self:
            unit.pricing = unit.building_area * unit.price_per_meter

    def make_reservation(self):
        for unit_obj in self:
            code = unit_obj.code
            building_unit = unit_obj.id
            address = unit_obj.address
            floor = unit_obj.floor
            pricing = unit_obj.pricing
            type = unit_obj.ptype.id
            status = unit_obj.status.id
            building = unit_obj.building_id.id
            building_code = unit_obj.building_id.code
            city = unit_obj.city_id.id
            region = unit_obj.region_id.id
            country = unit_obj.country_id.id
            building_area = unit_obj.building_area
            income_acc = unit_obj.account_income.id
            analytic_acc = unit_obj.account_analytic_id.id

            # awd
        vals = {'country': country, 'region': region, 'city': city, 'building_code': building_code,
                'building': building, 'unit_code': code, 'floor': floor, 'pricing': pricing,
                'type': type, 'address': address, 'status': status,
                'building_area': building_area, 'building_unit': building_unit,
                'account_income': income_acc, 'account_analytic_id': analytic_acc
                }

        reservation_obj = self.env['unit.reservation']
        reservation_id = reservation_obj.create(vals)
        mod_obj = self.env['ir.model.data']
        res = mod_obj.get_object_reference('itsys_real_estate', 'unit_reservation_form_view')
        res_id = res and res[1] or False
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'unit.reservation',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': reservation_id.id,
        }
