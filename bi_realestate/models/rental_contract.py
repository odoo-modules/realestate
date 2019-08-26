# -*- coding: utf-8 -*- 
from odoo import api, fields, models 
from datetime import datetime, timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta as rela
from odoo.tools.translate import _
from datetime import date as DA


# import DATE, YEAR, MONTH, DAY


class RentalContractInherit(models.Model):
    _inherit = "rental.contract"

    template_id = fields.Many2one('installment.template','Payment Template',required=True)


    @api.onchange('template_id','date_from','date_to','rental_fee','insurance_fee')
    def onchange_tmpl(self):
        if self.template_id:
            if self.date_from and self.date_to and self.rental_fee and self.insurance_fee:
                loan_lines = self._prepare_lines(self.date_from, self.date_to)
                self.loan_line= loan_lines

    def _prepare_lines(self, start_date, end_date):
        date1 = datetime.strptime(str(start_date), '%Y-%m-%d')
        date2 = datetime.strptime(str(end_date), '%Y-%m-%d')
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print(start_date[5:7])
        # print(start_date[8:10])
        # print("                 ")
        # print("                 ")
        # dedo = DA(int(end_date[:4]),int(end_date[5:7]),int(end_date[8:10])) - DA(int(start_date[:4]),int(start_date[5:7]),int(start_date[8:10]))

        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print(dedo)
        # print(dedo.days)
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        # print("                 ")
        r = relativedelta.relativedelta(date2, date1)
        total_mons = r.months
        total_days = r.days
        days_rent = 0
        if total_days >= 29:
            total_mons += 1
            total_days = 0
        else:
            days_rent = (self.rental_fee / 30) * total_days
        repeat = self.template_id.repetition_rate
        months_rpt = (total_mons // repeat)
        actual_rent = self.rental_fee * repeat
        total_rent = self.rental_fee * total_mons + days_rent
        remaining_fee = 0
        if (total_mons / repeat) > float(months_rpt):
            remaining = total_mons - (months_rpt * repeat)
            remaining_fee = self.rental_fee * remaining
        i = 1
        lines = [(0,0,{'serial':0,'amount':self.insurance_fee,'date': start_date,'name':_('Insurance Fees')})]
        first_installment = True
        date = date1 + rela(months=+repeat)
        for mon in range(months_rpt):
            if first_installment:
                lines.append((0,0,{'serial':i,'amount':actual_rent,'date': start_date,'name':_('Rental Fees')}))
                i += 1
                first_installment = False
            else:
                lines.append((0,0,{'serial':i,'amount':actual_rent,'date': date,'name':_('Rental Fees')}))
                i += 1
                date = date + rela(months=+repeat)
        if remaining_fee:
            fee = remaining_fee + days_rent
            lines.append((0,0,{'serial':i,'amount':fee,'date': date,'name':_('Rental Fees')}))
            i += 1

        return lines

    def action_confirm(self):
        for contract_obj in self:
            unit = contract_obj.building_unit
            unit.write({'state': 'reserved'})
        #self.prepare_lines()   
        self.generate_entries()     
        self.write({'state':'confirmed'})

    # def action_cancel(self):
    #     for contract_obj in self:
    #         unit = contract_obj.building_unit
    #         unit.write({'state':  'free'})
    #     # self.generate_cancel_entries()        
    #     self.write({'state':'cancel'})