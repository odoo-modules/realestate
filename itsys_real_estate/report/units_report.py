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
from odoo import api, fields, models, tools
from odoo import api, fields, models 

class report_units(models.Model):
    _name = "units.report"
    _description = "Units Statistics"
    _auto = False
    
    partner_id= fields.Many2one('res.partner','Owner', )
    building_id= fields.Many2one('building','Building', )
    nbr= fields.Integer('# Units', readonly=True)  
    desc= fields.Many2one('building.desc','Building Description', )
    city= fields.Many2one('cities','City', )
    rooms= fields.Char    ('Rooms', size=32 )
    type= fields.Many2one('building.type','Building Unit Type', )
    state= fields.Many2one('building.status','Building Unit Status', )
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
