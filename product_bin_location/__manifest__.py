# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Bin Location',
    'version': '1.1',
    'category': 'sale',
    'license': 'AGPL-3',
    'description': """
This is a module to add the default bin location in product.
And to add some new generic fields
==============================================
""",
    'author': 'Confianz Global,Inc.',
    'website': 'https://www.confianzit.com',
    'depends': ['stock'],
    'data': [  
        'views/product.xml',
      
    ],
    'demo': [  ],
    
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [],
}
