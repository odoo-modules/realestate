# -*- coding: utf-8 -*-
{
    'name': "Real Estate Custom",

    'summary': """Real Estate Customization""",

    'description': """
        Real Estate Customization
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Real Estate',
    'version': '2.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'bi_realestate', 'account_check_payment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/crm_lead.xml',
        'views/building_unit_view_inh.xml',
        'views/ownership_contract_view_inh.xml',
        'views/unit_reservation_inh.xml',
        'views/payment_check.xml',
        'views/rescheduling.xml',
        'wizard/settings.xml',
        'views/ir_cron.xml',
        'wizard/refund.xml',
        'wizard/due_installment.xml',
        'views/installment_template.xml',
        'views/loan_line_rs_own.xml',
        'views/res_partner.xml',
        'wizard/all_installment.xml',
        'report/all_installment_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
