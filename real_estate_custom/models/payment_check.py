# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta


class PaymentChecks(models.TransientModel):
    _inherit = 'customer.payment.check'

    check_ids = fields.One2many(comodel_name="check.transfer", inverse_name="payment_id", string="Checks",
                                required=False, )
    type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('receive_check', 'Received Check'),
        ('issue_check', 'Issue Check'),
        ('general', 'Miscellaneous')], related='journal.type')


    def create_check(self):
        if self.check_ids and not len(self.check_ids.ids) > 1:
            check_ids = self.env['check.payment.transaction'].sudo()
            for line in self.check_ids:
                check_vals = {
                    'check_name': line.check_name,
                    'check_number': line.check_number,
                    'partner_id': self.partner.id,
                    'journal_id': self.journal.id,
                    'bank_id': line.bank_id.id,
                    'amount': line.amount,
                    'check_payment_date': line.check_payment_date,
                    'check_issue_date': line.check_issue_date,
                    'payment_type': 'inbound',
                    'analytic_account_id': self.contract.account_analytic_id.id,
                }
                check_ids |= self.env['check.payment.transaction'].sudo().create(check_vals)
            return check_ids
        return None

    def check_lines(self):
        if self.journal.type == 'receive_check':
            if len(self.check_ids.ids) > 1:
                raise exceptions.ValidationError('You Can not create more than one check !')
            total_check_amount = 0
            for check in self.check_ids:
                total_check_amount += check.amount
            total_loan_amount = 0
            for loan in self.loan_line.filtered(lambda loan: loan.to_be_paid == True):
                if loan.discount_cash > 0:
                    total_loan_amount += (loan.input_amount - loan.discount_cash)
                elif loan.discount_percent > 0:
                    total_loan_amount += (loan.input_amount - ((loan.discount_percent / 100) * loan.input_amount))
                else:
                    total_loan_amount += loan.input_amount
            if round(total_check_amount, 2) != round(total_loan_amount, 2):
                raise exceptions.ValidationError('Checks amounts must equal loans input amounts !')

    def apply_discount(self, rec):
        lines_discount = 0
        total_amount = 0
        for line in rec.loan_line:
            if line.to_be_paid:
                lines_discount += (line.amount * line.discount_percent) / 100.0 + line.discount_cash
                total_amount += line.amount
        total_discount = total_amount * rec.discount_percent_total / 100.0 + rec.discount_cash_total
        total_discount += lines_discount

        if total_discount > 0:
            voucher_line_obj = self.env['account.voucher.line']
            default_discount_account = self.env['res.config.settings'].browse(
                self.env['res.config.settings'].search([])[-1].id).default_discount_account.id if self.env[
                'res.config.settings'].search([]) else ""
            if not default_discount_account:
                raise exceptions.ValidationError(_('Please set default Discount Account!'))
            voucher_id = self.create_voucher(rec, type='purchase')
            voucher_line_obj.create({
                'voucher_id': voucher_id.id,
                'name': 'Allowed Discount',
                'price_unit': total_discount,
                'account_id': default_discount_account,
                'account_analytic_id': rec.contract.account_analytic_id.id,
            })
            return voucher_id.id

    def check_input_amount(self):
        for line in self.loan_line:
            if line.to_be_paid and line.input_amount > line.due_amount:
                raise exceptions.ValidationError('Input Amount Can Not Be > Due Amount !')

    def pay(self):
        if self.journal.type == 'receive_check':
            self.check_lines()
            if self.check_ids and self.loan_line:
                penalty_obj = self.env['late.payment.penalties']
                voucher_line_obj = self.env['account.voucher.line']
                line_ids = []
                total_penalties = 0
                for line in self.loan_line:
                    if line.to_be_paid:
                        total_penalties += penalty_obj.get_penalties(line)
                        line_ids.append(line.installment_line_id)
                if line_ids:
                    if not self.contract.partner_id.property_account_receivable_id.id:
                        raise exceptions.UserError(_('Please set receivable account for Partner'))
                    check_id = self.create_check()
                    loan_line_rs_own_obj = self.env['loan.line.rs.own'].browse(line_ids)
                    for line in loan_line_rs_own_obj:
                        self.contract.get_commission_paid(line.input_amount, line.date)
                    check_id.loan_ids = loan_line_rs_own_obj
                    discount_voucher = self.apply_discount(self)
        else:
            self.check_input_amount()
            penalty_obj = self.env['late.payment.penalties']
            voucher_line_obj = self.env['account.voucher.line']
            line_ids = []
            total_penalties = 0
            if self.payment_method == 'cash':
                to_be_paid = False
                if True in self.loan_line.mapped('to_be_paid'):
                    to_be_paid = True
                if to_be_paid:
                    if not self.contract.partner_id.property_account_receivable_id.id:
                        raise exceptions.UserError(_('Please set receivable account for Partner'))
                    voucher_id = self.create_voucher(self, type='sale')
                    for line in self.loan_line:
                        if line.to_be_paid:
                            total_penalties += penalty_obj.get_penalties(line)
                            name = str(' Regarding Ownership Contract ') + str(self.contract.name) + " # " + line.installment_line_id.serial
                            voucher_line_obj.create({
                                'installment_line_id': line.installment_line_id.id,
                                'voucher_id': voucher_id.id,
                                'name': name,
                                'price_unit': line.input_amount,
                                'account_id': self.contract.partner_id.property_account_receivable_id.id,
                                'account_analytic_id': self.contract.account_analytic_id.id,
                            })
                            self.contract.get_commission_paid(line.input_amount, line.date)
                    vouchers = []
                    discount_voucher = self.apply_discount(self)
                    if discount_voucher: vouchers.append(discount_voucher)
                    vouchers.append(voucher_id.id)
                    if total_penalties > 0:
                        penalty_str = str(' Penalty on Ownership Contract ') + str(
                            self.contract.name) + " # " + line.serial
                        voucher_line_obj.create({
                            'voucher_id': voucher_id.id,
                            'name': penalty_str,
                            'price_unit': total_penalties,
                            'account_id': penalty_obj.get_account(),
                            'account_analytic_id': self.contract.account_analytic_id.id,
                        })
                    return {
                        'name': _('Vouchers'),
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'domain': [('id', 'in', vouchers)],
                        'res_model': 'account.voucher',
                        'type': 'ir.actions.act_window',
                        'nodestroy': True,
                        'target': 'current',
                    }
            # can be activated in case of receiving cheques
            if self.payment_method == 'cheque':
                lines_discount = 0
                total_amount = 0
                for rec in self:
                    total_to_be_paid = 0
                    for line in rec.loan_line:
                        if line.to_be_paid:
                            lines_discount += (line.amount * line.discount_percent) + line.discount_cash
                            total_amount += line.amount
                            total_penalties += penalty_obj.get_penalties(line)
                            line_ids.append(line.installment_line_id)
                            total_to_be_paid += total_penalties
                    if line_ids:
                        if not rec.contract.partner_id.property_account_receivable_id.id:
                            raise exceptions.UserError(_('Please set receivable account for Partner'))
                        loan_line_rs_own_obj = self.env['loan.line.rs.own'].browse(line_ids)
                        for line in loan_line_rs_own_obj:
                            line.write({'paid': True})
                            total_to_be_paid += line.amount
                    total_discount = total_amount * rec.discount_percent_total + rec.discount_cash_total
                    total_discount += lines_discount
                    total_to_be_paid += total_discount

                    abs_pool = self.env['account.bank.statement']
                    abs_line_pool = self.env['account.bank.statement.line']
                    abs_id = abs_pool.create({
                        'real_estate_ref': rec.contract.name,
                        'partner_id': rec.contract.partner_id.id,
                        'journal_id': rec.journal.id,
                        'collect_ok': True,
                        'ref': rec.cheque_number,
                    })
                    abs_line_pool.create({'partner_id': rec.contract.partner_id.id,
                                          'statement_id': abs_id,
                                          'amount': total_to_be_paid,
                                          'ref': rec.cheque_number,
                                          'name': 'Regarding Ownership Contract #' + str(rec.contract.name)
                                          })

                    mod_obj = self.env['ir.model.data']
                    res = mod_obj.get_object_reference('bank_statement_mod', 'view_bank_statement_form_collect')
                    res_id = res and res[1] or False
                    return {
                        'view_type': 'form',
                        'view_mode': 'form',
                        'view_id': [res_id],
                        'res_model': 'account.bank.statement',
                        'type': 'ir.actions.act_window',
                        'nodestroy': True,
                        'target': 'current',
                        'res_id': abs_id,
                    }


class Checks(models.Model):
    _inherit = 'check.payment.transaction'

    loan_ids = fields.Many2many(comodel_name="loan.line.rs.own", string="Loans", )

    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash', 'receive_check'))])

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    @api.multi
    def action_receive(self):
        for rec in self:
            if rec.state != 'draft':
                raise exceptions.UserError(_("Only a check with status draft can be received."))

            company_id = rec.company_id or self.env.user.company_id
            currency_id = company_id.currency_id

            debit_account = rec.journal_id.default_debit_account_id.id
            credit_account = rec.partner_id.property_account_receivable_id.id

            if not debit_account:
                raise exceptions.UserError(_("You should define Debit Account for this Journal"))
            if not credit_account:
                raise exceptions.UserError(_("You should define Credit Account for this Partner"))
            move = {
                'journal_id': rec.journal_id.id,
                'ref': '',
                'company_id': company_id.id,
                'name': rec.journal_id.sequence_id.with_context(
                    ir_sequence_date=str(date.today())).next_by_id()

            }

            move_line = {
                'name': 'Check Transfer:' + rec.check_name + 'Number:' + str(self.check_number),
                'ref': '',
                'date': date.today(),
                'partner_id': rec.partner_id.id,
            }
            B = self.sudo().env['create.rent.moves'].create_move_lines(move=move, move_line=move_line,
                                                                       debit_account=debit_account,
                                                                       credit_account=credit_account,
                                                                       src_currency=currency_id,
                                                                       amount=rec.amount,
                                                                       analytic_account=rec.analytic_account_id.id
                                                                       )
            rec.name = rec.check_name + ' ' + rec.check_number
            for loan in rec.loan_ids:
                loan.write({'paid': True})
            rec.write({'state': 'received'})
