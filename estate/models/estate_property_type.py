from odoo import fields, models, api


class EstatePropertyType(models.Model):

    _name = 'estate.property.type'
    _description = 'Real Estate Property Type'
    _order = 'sequence, name'
    _sql_constraints = [
        ('check_name', 'UNIQUE (name)', 'The type name must be unique'),
    ]

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence', default=1)

    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')

    offer_count = fields.Integer('Offers Count', compute='_compute_offer_count')

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
