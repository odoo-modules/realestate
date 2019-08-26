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

from datetime import datetime, timedelta
import time
from odoo import api, fields, models 

class building(models.Model):
    _name = "building"
    _description = "Building"
    _inherit = ['mail.thread']

    region_id= fields.Many2one('regions','Region', )
    city_id= fields.Many2one('cities', string='City', related='region_id.city_id', store=True, readonly=True)
    country_id= fields.Many2one('countries', string='Country', related='region_id.city_id.country_id', store=True, readonly=True)
    account_income= fields.Many2one('account.account','Income Account', )
    account_analytic_id= fields.Many2one('account.analytic.account', 'Analytic Account')
    #'multi_images_view= fields.One2many('multi.images.building', 'building_id_chart',
    #                                  'Multi Images')
    active= fields.Boolean ('Active', help="If the active field is set to False, it will allow you to hide the top without removing it.",default=True)
    #'account_analytic_id= fields.Many2one('account.analytic.account', 'Analytic Account')
    # 'analytic_line_ids= one2many_analytic('account.analytic.line', 'account_id', 'Analytic Lines')
    alarm= fields.Boolean ('Alarm')
    old_building= fields.Boolean ('Old Building')
    constructed= fields.Integer ('Construction Year')
    #blueprint= fields.binary  ('Blueprint')
    category= fields.Char    ('Category', size=16)
    description= fields.Text    ('Description')
    floor= fields.Char    ('Floor', size=16)
    pricing= fields.Integer   ('Price',)
    balcony= fields.Integer   ('Balconies m²',)
    building_area= fields.Integer   ('Building Area m²',)
    land_area= fields.Integer   ('Land Area m²',)
    garden= fields.Integer   ('Garden m²',)
    terrace= fields.Integer   ('Terraces m²',)
    garage= fields.Integer ('Garage included')
    carport= fields.Integer ('Carport included')
    parking_place_rentable= fields.Boolean ('Parking rentable', help="Parking rentable in the location if available")
    handicap= fields.Boolean ('Handicap Accessible')
    heating= fields.Selection([('unknown','unknown'),
                                           ('none','none'),
                                           ('tiled_stove', 'tiled stove'),
                                           ('stove', 'stove'),
                                           ('central','central heating'),
                                           ('self_contained_central','self-contained central heating')], 'Heating')
    heating_source= fields.Selection([('unknown','unknown'),
                                           ('electricity','Electricity'),
                                           ('wood','Wood'),
                                           ('pellets','Pellets'),
                                           ('oil','Oil'),
                                           ('gas','Gas'),
                                           ('district','District Heating')], 'Heating Source')
    internet= fields.Boolean ('Internet')
    lease_target= fields.Integer   ('Target Lease', )
    lift= fields.Boolean ('Lift')
    name= fields.Char    ('Name', size=64, required=True)
    code= fields.Char    ('Code', size=16)
    note= fields.Html    ('Notes')
    note_sales= fields.Text    ('Note Sales Folder')
    partner_id= fields.Many2one('res.partner','Owner', )
    type= fields.Many2one('building.type','Building Type', )
    status= fields.Many2one('building.status','Building Status', )
    city= fields.Many2one('cities','City', )
    partner_from= fields.Date    ('Purchase Date')
    partner_to= fields.Date    ('Sale Date')
    rooms= fields.Char    ('Rooms', size=32 )
    solar_electric= fields.Boolean ('Solar Electric System')
    solar_heating= fields.Boolean ('Solar Heating System')
    staircase= fields.Char    ('Staircase', size=8)
    surface= fields.Integer   ('Surface')
    telephon= fields.Boolean ('Telephon')
    tv_cable= fields.Boolean ('Cable TV')
    tv_sat= fields.Boolean ('SAT TV')
    usage= fields.Selection([('unlimited','unlimited'),
                                          ('office','Office'),
                                           ('shop','Shop'),
                                           ('flat','Flat'),
                                            ('rural','Rural Property'),
                                           ('parking','Parking')], 'Usage')
    product_product_id= fields.Integer ('Product')
    sort= fields.Integer ('Sort')
    sequence= fields.Integer ('Sequ.')
    air_condition= fields.Selection([('unknown','Unknown'),
                                           ('none','None'),
                                           ('full','Full'),
                                           ('partial','Partial'),
                                           ], 'Air Condition' )
    address= fields.Char    ('Address')
    license_code= fields.Char    ('License Code', size=16)
    license_date= fields.Date    ('License Date')
    date_added= fields.Date    ('Date Added to Notarization')
    license_location= fields.Char    ('License Notarization')
    electricity_meter= fields.Char    ('Electricity meter', size=16)
    water_meter= fields.Char    ('Water meter', size=16)
    north= fields.Char    ('Northen border by:')
    south= fields.Char    ('Southern border by:')
    east= fields.Char    ('Eastern border  by: ')
    west= fields.Char    ('Western border by: ')

    _sql_constraints = [
        ('unique_building_code', 'UNIQUE (code,region_id,city_id,country_id)', 'Building code must be unique!'),
    ]