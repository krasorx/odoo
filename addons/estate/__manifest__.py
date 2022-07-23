# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Real Estate',
    'category': 'Marketing',
    'sequence': -100,
    'author': 'Goku',
    'license': 'LGPL-3',
    'description': """
    haber osea digamos """,
    'application': True,
     'depends': [],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_offers_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_menus.xml', 
        'views/estate_property_payment.xml',
        'report/estate_property_templates.xml',
        'report/estate_property_reports.xml',
    ]
}