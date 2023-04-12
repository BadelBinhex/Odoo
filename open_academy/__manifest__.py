# -*- coding: utf-8 -*-
{
    'name': "Open Academy",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Aplication made by Badel which can register courses.
    """,

    'author': "Badel Bonilla Simón",
    'website': "http://www.yourcompany.com",
    'application':True,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'board','portal'],

    # always loaded
    'data': [
        'security/seguridad.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/dashboard.xml',
        'views/reports.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
