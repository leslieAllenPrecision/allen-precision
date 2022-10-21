# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ups Multi Package',
    'version': '1.0',
    'category': 'sale',
    'license': 'AGPL-3',
    'description': """
This is a module to add the multi pacakge functionality in ups
==============================================
""",
    'author': 'Confianz Global,Inc.',
    'website': 'https://www.confianzit.com',
    'depends': ['ape_fixes','delivery_ups'],
    'data': [  
        'security/ir.model.access.csv',
        'views/sale.xml',
        'views/picking.xml'
    ],
    'demo': [  ],
    
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [],
}