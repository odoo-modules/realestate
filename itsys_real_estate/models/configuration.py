# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# -*- coding: utf-8 -*-
from ast import literal_eval

from odoo import api, fields, models

class real_estate_setings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    default_reservation_hours= fields.Integer(string='Hours to release units reservation',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).default_reservation_hours if self.env['res.config.settings'].search([]) else "")
    default_penalty_percent= fields.Integer ('Penalty Percentage',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).default_penalty_percent if self.env['res.config.settings'].search([]) else "")
    default_penalty_account= fields.Many2one('account.account','Late Payments Penalty Account',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).default_penalty_account.id if self.env['res.config.settings'].search([]) else "")
    default_discount_account= fields.Many2one('account.account','Discount Account',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).default_discount_account.id if self.env['res.config.settings'].search([]) else "")
    default_income_account= fields.Many2one('account.account','Income Account',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).default_income_account.id if self.env['res.config.settings'].search([]) else "")
    default_me_account= fields.Many2one('account.account','Managerial Expenses Account',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).default_me_account.id if self.env['res.config.settings'].search([]) else "")
    default_analytic_account= fields.Many2one('account.analytic.account','Analytic Account',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).default_analytic_account.id if self.env['res.config.settings'].search([]) else "")

class Config(models.TransientModel):
    _name = 'gmap.config'

    @api.model
    def get_key_api(self):
        return self.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')