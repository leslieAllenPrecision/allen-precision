# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'APE FIXES',
    'version': '2.3',
    'category': 'sale',
    'license': 'AGPL-3',
    'description': """
This is a module to fix some the core base things.
And to add some new generic fields
==============================================
""",
    'author': 'Confianz Global,Inc.',
    'website': 'https://www.confianzit.com',
    'depends': ['sale_management','stock','sale','delivery','account_reports','l10n_us_check_printing'],
    'data': [  
       'views/res_partner_view.xml',
       'views/sale_view.xml',
       'views/account_view.xml',
       'views/picking_view.xml',
       'views/print_check.xml',
       'views/inventory_report.xml',
    ],
    'demo': [  ],
    
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [],
}
