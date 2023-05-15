# -*- coding: utf-8 -*-
{
    # App information
    'name': 'Repair Custom',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'license': '',
    'description': """This module is used to add custom fields and logic to the repair application""",
    # Author
    'author': '',
    'website': '',
    'maintainer': '',
    # Dependencies
    'depends': ['repair'],
    # Views
    'data': [
        'report/repair_report.xml',
        'views/repair.xml',
    ],
    # Odoo Store Specific
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [],
}
