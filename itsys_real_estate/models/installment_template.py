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

class installment_template(models.Model):
    _name = "installment.template"
    _description = "Installment Template"
    _inherit = ['mail.thread']

    name= fields.Char    ('Name', size=64, required=True)
    duration_month= fields.Integer   ('Month')        
    duration_year= fields.Integer   ('Year')        
    annual_raise= fields.Integer   ('Annual Raise %')        
    repetition_rate= fields.Integer   ('Repetition Rate (month)', default=1)        
    adv_payment_rate= fields.Integer   ('Advance Payment %')        
    deduct= fields.Boolean   ('Deducted from amount?')            