# -*- coding: utf-8 -*-
from odoo import exceptions
from odoo import api, fields, models 
from odoo.tools.translate import _
import time
import datetime
from datetime import datetime, date,timedelta
from dateutil import relativedelta

class occupancy_check(models.TransientModel):
    _name = 'occupancy.check'
    
    city_check= fields.Boolean('Filter by city')
    region_check= fields.Boolean('Filter by region')
    building_check= fields.Boolean('Filter by building')
    unit_check= fields.Boolean('Filter by building unit')

    city_ids= fields.Many2many('cities', string='City',
                                     help="Only selected cities will be printed. "
                                          "Leave empty to print all cities.")
    region_ids= fields.Many2many('regions', string='Region',
                                     help="Only selected Regions will be printed. "
                                          "Leave empty to print all Regions.")
    building_ids= fields.Many2many('building', string='Building',
                                     help="Only selected building will be printed. "
                                          "Leave empty to print all building.")
    unit_ids= fields.Many2many('product.template',domain=[('is_property', '=', True)], string='Building Unit',
                                     help="Only selected building unit will be printed. "
                                          "Leave empty to print all building unit.")

    @api.multi
    def check_report(self):
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'product.template',
            'form': data
        }
        return self.env.ref('itsys_real_estate.report_unit_occupancy').report_action([],data=datas)

