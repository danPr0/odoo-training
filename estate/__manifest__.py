{
    'name': 'Estate',
    'category': 'Real Estate/Brokerage',
    'depends': [
        'base',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/estate_property_offer_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',
        'report/estate_reports.xml',
        'report/estate_report_views.xml',
        'data/estate.property.type.csv',
        'demo/estate_property_tag.xml',
        'demo/estate_property.xml',
        'demo/estate_property_offer.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
