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
from odoo.tools.translate import _

class building_unit(models.Model):
    # _name = "product.template"
    _inherit = ['product.template']
    _description = "Property"

    def view_reservations(self):
        reservation_obj = self.env['unit.reservation']
        reservations_ids = reservation_obj.search([('building_unit', '=', self.ids)])
        reservations=[]
        for obj in reservations_ids: reservations.append(obj.id)
        return {
            'name': _('Reservation'),
            'domain': [('id', 'in', reservations)],
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'unit.reservation',
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'view_id': False,
            'target':'current',
        }

    def _reservation_count(self):
        reservation_obj = self.env['unit.reservation']
        for unit in self:
            reservations_ids = reservation_obj.search([('building_unit', '=', unit.id)])    
            unit.reservation_count = len(reservations_ids)

    url= fields.Char ('Website URL')
    website_published= fields.Boolean ('Website Published',default=True)
    lng= fields.Float   ('Longitude')
    lat= fields.Float   ('Latitude')
    is_property= fields.Boolean ('Property')
    contacts= fields.Many2many('res.partner',string='Contacts')
    building_id= fields.Many2one('building','Building')
    region_id= fields.Many2one('regions', string='Region', related='building_id.region_id', store=True, readonly=True)
    city_id= fields.Many2one('cities', string='City', related='building_id.region_id.city_id', store=True, readonly=True)
    country_id= fields.Many2one('countries', string='Country', related='building_id.region_id.city_id.country_id', store=True, readonly=True)
    component_ids= fields.One2many('components.line', 'unit_id', string='Components List')
    reservation_count= fields.Integer(compute='_reservation_count',string='Reservation Count',)        
    cnt= fields.Integer   ('Count',default=1)
    unit_status2= fields.Char    ('Status', size=16)
    active= fields.Boolean ('Active', help="If the active field is set to False, it will allow you to hide the top without removing it.",default=True)
    # 'analytic_line_ids'  : one2many_analytic('account.analytic.line', 'account_id', 'Analytic Lines')
    alarm= fields.Boolean ('Alarm')
    old_building= fields.Boolean ('Old Building')
    constructed= fields.Integer ('Construction Year')
    #blueprint= fields.binary  ('Blueprint')
    category= fields.Char    ('Category', size=16)
    description= fields.Text    ('Description')
    floor= fields.Char    ('Floor', size=16)
    pricing= fields.Integer   ('Price',)
    balcony= fields.Integer   ('Balconies m²',)
    building_area= fields.Integer   ('Building Unit Area m²',)
    building_area_net= fields.Integer   ('Net Area m²',)
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
                                           ('self_contained_central','self-contained central heating')], 'Heating',)
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
    code= fields.Char    ('Code', size=16, required=True)
    note= fields.Html    ('Notes')
    note_sales= fields.Text    ('Note Sales Folder')
    partner_id= fields.Many2one('res.partner','Owner')
    ptype= fields.Many2one('building.type','Building Unit Type')
    status= fields.Many2one('building.status','Unit Status')
    desc= fields.Many2one('building.desc','Description')
    city= fields.Many2one('cities','City')
    partner_from= fields.Date    ('Purchase Date')
    partner_to= fields.Date    ('Sale Date')
    rooms= fields.Char    ('Rooms', size=32 )
    solar_electric= fields.Boolean ('Solar Electric System')
    solar_heating= fields.Boolean ('Solar Heating System')
    staircase= fields.Char    ('Staircase', size=8)
    surface= fields.Integer   ('Surface', )
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
                                           ('partial','Partial')
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
    east= fields.Char    ('Eastern border  by:')
    west= fields.Char    ('Western border by:')
    rental_fee= fields.Integer   ('Rental fee')
    insurance_fee= fields.Integer   ('Insurance fee')
    template_id= fields.Many2one('installment.template','Payment Template')
    state= fields.Selection([('free','Free'),
                               ('reserved','Reserved'),
                               ('sold','Sold'),
                               ('blocked','Blocked'),
                               ], 'State',default='free' )

    _sql_constraints = [
        ('unique_property_code', 'UNIQUE (code,building_id,region_id,city_id,country_id)', 'property code must be unique!'),
    ]

    def make_reservation(self):
        for unit_obj in self:
            code =  unit_obj.code
            building_unit =  unit_obj.id
            address =  unit_obj.address
            floor =  unit_obj.floor
            pricing =  unit_obj.pricing
            type =  unit_obj.ptype.id
            status =  unit_obj.status.id
            building =  unit_obj.building_id.id
            building_code =  unit_obj.building_id.code
            city =  unit_obj.city_id.id
            region =  unit_obj.region_id.id
            country =  unit_obj.country_id.id
            building_area =  unit_obj.building_area
            
        vals= {'country':country,'region':region,'city':city,'building_code':building_code,
               'building':building,'unit_code': code,'floor': floor,'pricing': pricing,
               'type': type,'address': address,'status': status,
               'building_area': building_area,'building_unit':building_unit}

        reservation_obj = self.env['unit.reservation']        
        reservation_id = reservation_obj.create(vals)
        mod_obj = self.env['ir.model.data']
        res = mod_obj.get_object_reference('itsys_real_estate', 'unit_reservation_form_view')
        res_id = res and res[1] or False
        return {
            'view_type':'form',
            'view_mode':'form',
            'view_id':[res_id],
            'res_model':'unit.reservation',
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'target':'current',
            'res_id': reservation_id.id,
        }

class components_line(models.Model):
    _name = "components.line"    
    component= fields.Many2one('component','Components', required=True)
    unit_id= fields.Many2one('product.template', 'Building Unit View',domain=[('is_property', '=', True)])
    

class component(models.Model):
    _name = "component"
    name= fields.Char('Name', required=True)
    furniture_details_ids= fields.One2many('furniture', 'component_id', string='Furniture List')

class furniture(models.Model):
    _name = "furniture"    
    product_id= fields.Many2one('product.product','Furniture',required=True)
    component_id= fields.Many2one('component', 'Component View')

class product_template(models.Model):
    _inherit = "product.template"
    furniture= fields.Boolean('Furniture')
    
