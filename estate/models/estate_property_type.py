from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real estate property types'

    name = fields.Char(required=True)

    _sql_constraints = [('unique_property_type_name', 'UNIQUE (name)', 'The type name must be unique')]
