# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Proyecto SP',
    'category': 'Marketing',
    'sequence': -100,
    'author': 'Goku',
    'license': 'LGPL-3',
    'description': """
    haber osea digamos """,
    'application': True,
    'depends': [
        'mail',
        'contacts',
        ],
     
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/email_reserve_template.xml',
        'data/sequence_data.xml',
        'data/kroni.xml',
        'views/estate_offers_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_menus.xml', 
        'report/estate_property_templates.xml',
        'report/estate_property_reports.xml',
        'report/estate_property_template_contract.xml',
    ],
    'css': ['static/src/css/sp.css']
}