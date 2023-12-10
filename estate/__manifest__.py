{
    'name': 'Estate',
    'category': 'Real Estate/Brokerage',
    'depends': [
        'base',
    ],
    'data': [
        'security/estate_groups.xml',
        'security/estate_property_security.xml',
        'security/ir.model.access.csv',
        'views/estate_property_offer_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',
        'report/estate_templates.xml',
        'report/estate_reports.xml',
        'data/estate.property.type.data.csv',
        'data/estate_property_tag_demo.xml',
        'data/estate_property_demo.xml',
        'data/estate_property_offer_demo.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
