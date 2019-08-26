# -*- coding: utf-8 -*-
from odoo import exceptions
from odoo import api, fields, models 
from odoo.tools.translate import _
import time
import datetime
from datetime import datetime, date,timedelta
from dateutil import relativedelta

class late_payment_unit_check(models.TransientModel):
    _name = 'late.payment.unit.check'
    
    date_start= fields.Date('From',required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_end= fields.Date('To',required=True, default= lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],)
    building_unit= fields.Many2many('product.template',domain=[('is_property', '=', True)], string='Filter on units',
                                     help="Only selected units will be printed. "
                                          "Leave empty to print all units.")

    @api.multi
    def check_report(self):
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'ownership.contract',
            'form': data
        }
        return self.env.ref('itsys_real_estate.late_payments_units').report_action([],data=datas)