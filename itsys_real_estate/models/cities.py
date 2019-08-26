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

from odoo import api, fields, models

class cities(models.Model):
    _name = "cities"
    _inherit = ['mail.thread']
    _description = "City"
    _parent_name = "city_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'
    _rec_name = 'complete_name'

    @api.one
    @api.depends('name', 'city_id.complete_name')
    def _compute_complete_name(self):
        """ Forms complete name of location from parent location to child location. """
        if self.city_id.complete_name:
            self.complete_name = '%s/%s' % (self.city_id.complete_name, self.name)
        else:
            self.complete_name = self.name

    name= fields.Char ('Name',required=True)
    complete_name = fields.Char("Full Name", compute='_compute_complete_name', store=True)

    child_ids= fields.One2many('cities', 'city_id', 'Contains')
    parent_left= fields.Integer('Left Parent', index=True)
    parent_right= fields.Integer('Right Parent', index=True)
    country_id= fields.Many2one('countries','Country', )
    city_id= fields.Many2one('cities','Parent City', ondelete='cascade')
    population_density= fields.Integer('Population Density')
    land_area= fields.Integer('Land Area m²')
    type= fields.Many2one('cities.type','Type', )
    latlng_ids= fields.One2many('latlng.line', 'city_id', string='LatLng List',copy=True)
    map= fields.Char('Map', digits=(9, 6))


class cities_type(models.Model):
    _name = "cities.type"
    name= fields.Char ('Name')

class latlng_line(models.Model):
    _name = "latlng.line"
    lat= fields.Float('Latitude', digits=(9, 6),required=True)
    lng= fields.Float('Longitude', digits=(9, 6),required=True)
    url= fields.Char('URL', digits=(9, 6),required=True)
    city_id= fields.Many2one('cities', 'City')
    unit_id= fields.Many2one('product.template', 'Unit',domain=[('is_property', '=', True)])
    state= fields.Selection(string='State', related='unit_id.state', store=True, readonly=True)

    @api.onchange('url')
    def onchange_url(self):
        if self.url:
            url = self.url
            self.unit_id= int (((url.split("#")[1]).split("&")[0]).split("=")[1])
        else:
            self.unit_id=None
            self.state=None