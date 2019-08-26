# -*- coding: utf-8 -*-
from odoo import exceptions
from odoo import api, fields, models 
from odoo.tools.translate import _
import time
import datetime
from datetime import datetime, date,timedelta
from dateutil import relativedelta

class due_payment_check(models.TransientModel):
    _name = 'due.payment.check'
    
    date_start= fields.Date('From',required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_end= fields.Date('To',required=True, default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    partner_ids= fields.Many2many('res.partner', string='Filter on partner',
                                     help="Only selected partners will be printed. "
                                          "Leave empty to print all partners.")

    @api.multi
    def check_report(self):
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'ownership.contract',
            'form': data
        }
        return self.env.ref('itsys_real_estate.due_payments_customers').report_action([],data=datas)