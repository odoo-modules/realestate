# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta


class Reservation(models.Model):
    _inherit = 'unit.reservation'

    lead_id = fields.Many2one(comodel_name="crm.lead", string="CRM Lead", required=False, )


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    building_id = fields.Many2one(comodel_name="building", string="Building", required=False, )
    unit_id = fields.Many2one(comodel_name="product.template", string="Building Unit", required=False,
                              domain=[('id', '=', False)])
    unit_state = fields.Selection([('free', 'Free'),
                                   ('reserved', 'Reserved'),
                                   ('sold', 'Sold'),
                                   ('blocked', 'Blocked'),
                                   ], 'State', related='unit_id.state')

    reservation_ids = fields.One2many(comodel_name="unit.reservation", inverse_name="lead_id", string="Reservations",
                                      required=False, )
    reservation_count = fields.Integer(string="Reservations", required=False, compute="get_reservation_count")

    def action_create_reservation(self):
        return {
            'name': _('Unit Reservation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'unit.reservation',
            'target': 'current',
            'context': {
                'default_lead_id': self.id, 'default_partner_id': self.partner_id.id,
                'default_building': self.building_id.id,
                'default_building_unit': self.unit_id.id,
                'default_account_analytic_id': self.unit_id.account_analytic_id.id,
                'default_account_income': self.unit_id.account_income.id,
                'default_country': self.unit_id.country_id.id,
                'default_city': self.unit_id.city_id.id,
                'default_region': self.unit_id.region_id.id,
                'default_building_code': self.building_id.code,
            },
        }

    @api.onchange('building_id')
    def onchange_building_id(self):
        if self.building_id:
            return {
                'domain': {
                    'unit_id': [('building_id', '=', self.building_id.id), ('state', '=', 'free')]
                }
            }
        else:
            return {
                'domain': {
                    'unit_id': [('id', '=', False)]
                }
            }

    @api.depends('reservation_ids')
    def get_reservation_count(self):
        for line in self:
            line.reservation_count = len(line.reservation_ids.ids)

    def action_open_reservation(self):
        return {
            'name': _('Unit Reservation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'unit.reservation',
            'target': 'current',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id, 'default_partner_id': self.partner_id.id,
                        'default_building': self.building_id.id,
                        'default_building_unit': self.unit_id.id, },
        }
