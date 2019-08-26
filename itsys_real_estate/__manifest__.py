# -*- coding: utf-8 -*-
{
    'name':'Real Estate',
    'version':'1.0',
    'category':'Real Estate',
    'sequence':14,
    'summary':'',
    'description':""" Real Estate Management
      - Properties Hierarchy
      - Google Maps Integration
      - Units Reservation
      - Ownership Contracts Managament
      - Easy Tenant Management
      - Invoicing Management & Accounting Integration
      - Property Release
      - Property Refund
      - Email Notifications
      - Sales Commission for Users
      - Integration with Odoo Website
      - Comprehensive Reporting
      """,
    'author':'ITSYS CORPORATION, Fatma Yousef',
    'price':500,
    'currency':'EUR',
    'website':'https://www.it-syscorp.com',
    'depends':['base','account_voucher','website_sale'],
    'data':[
        'security/real_estate_security.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'wizard/sms_wizard_view.xml',
        'wizard/mail_wizard_view.xml',
        'wizard/duepayment.xml',
	    'wizard/salesperson_sales.xml',
        'wizard/duepaymentunit.xml',
        'wizard/latepayment.xml',
        'wizard/latepaymentunit.xml',
        'wizard/occupancy.xml',
        'wizard/realestate_pay.xml',
        'wizard/realestate_rental_pay.xml',
        'wizard/realestate_refund.xml',
        'views/building_view.xml',
        'views/cities.xml',
        'views/countries.xml',
        'views/regions.xml',
        'views/building_desc_view.xml',
        'views/building_status_view.xml',
        'views/building_type_view.xml',
        'views/building_unit_view.xml',
        'views/installment_template_view.xml',
        'views/partner_ssnbr_view.xml',
        'views/real_estate_payment_view.xml',
        'views/unit_release_view.xml',
        'views/unit_reservation_view.xml',
        'views/rental_contract_view.xml',
        'views/res_partner.xml',
        'views/ownership_contract_view.xml',
        'views/commission_view.xml',
        'views/due_payments_notification_view.xml',
        'views/real_estate_reports_view.xml',
        'views/configuration.xml',
        'views/template.xml',
        'views/product_view.xml',
        'views/product_template.xml',
        'views/website_config_view.xml',
        'sequences/ownership_contract_sequence.xml',
        'sequences/release_sequence.xml',
        'sequences/rental_contract_sequence.xml',
        'sequences/reservation_sequence.xml',
	    'report/report_sample.xml',
	    'report/templates/report_reservation.xml',
        'report/templates/report_ownership_contract.xml',
        'report/templates/report_release_contract.xml',
        'report/templates/rental_contract.xml',
	    'report/templates/sales_representatives.xml',
        'report/templates/occupany.xml',
        'report/templates/due_payments_customers.xml',
        'report/templates/due_payments_units.xml',
        'report/templates/late_payments_customers.xml',
	    'report/templates/late_payments_units.xml',
	    'report/templates/report_quittance_letter.xml',
        'report/ownership_contract_bi_report.xml',
        'report/rental_contract_bi_report.xml',
        'data/real_estate_demo.xml',
        'data/mail_template_data.xml',
        'data/website_data.xml',
    ],
    'images': ['static/description/images/splash-screen.jpg'],
    'installable':True,
    'auto_install':False,
    'application':True,
    'qweb': ['static/src/xml/*.xml'],
}
# AIzaSyAu47j0jBPU_4FmzkjA3xc_EKoOISrAJpI