# -*- coding: utf-8 -*-
from odoo import exceptions
from odoo import api, fields, models 
from odoo.tools.translate import _
import time
import datetime
from datetime import datetime, date,timedelta
from dateutil import relativedelta

class salesperson_sales_check(models.TransientModel):
    _name = 'salesperson.sales.check'
    
    date_from= fields.Date('From',required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to= fields.Date('To',required=True, default= lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],)

    user_ids= fields.Many2many('res.users', string='Salesperson',
                                 help="Only selected salespersons will be printed. "
                                      "Leave empty to print all salesperson.")

    @api.multi
    def check_report(self):
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'ownership.contract',
            'form': data
        }
        return self.env.ref('itsys_real_estate.report_sales_rep_rs').report_action([],data=datas)