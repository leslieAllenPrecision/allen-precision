# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'APE FIXES',
    'version': '1.4',
    'category': 'sale',
    'license': 'AGPL-3',
    'description': """
This is a module to fix some the core base things.
And to add some new generic fields
==============================================
""",
    'author': 'Confianz Global,Inc.',
    'website': 'https://www.confianzit.com',
    'depends': ['sale_management','sale','delivery','account_reports'],
    'data': [  
       'views/res_partner_view.xml',
       'views/sale_view.xml',
       'views/account_view.xml',
       'views/picking_view.xml'
    ],
    'demo': [  ],
    
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [],
}
