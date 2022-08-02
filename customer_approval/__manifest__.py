# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Customer Approval',
    'version': '1.1',
    'category': 'sale',
    'description': """
This is a customer approval module.
==============================================
    * Customer Approval
    * Order Validation
""",
    'author': 'Confianz Global,Inc.',
    'website': 'https://www.confianzit.com',
    'depends': ['sale'],
    'data': [  
        'security/customer_approval.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml'
    ],
    'demo': [  ],
    
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [],
}
