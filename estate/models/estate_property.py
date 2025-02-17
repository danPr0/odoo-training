from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'
    _order = 'id desc'
    _sql_constraints = [
        ('check_expected_price', 'CHECK ( expected_price > 0 )', 'The expected price must be strictly positive'),
        ('check_selling_price', 'CHECK ( selling_price >= 0 )', 'The selling price must be positive'),
    ]

    def _default_date_availability(self):
        return fields.Date.context_today(self) + relativedelta(months=3)

    name = fields.Char('Title', required=True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date(
        'Available From', default=lambda self: self._default_date_availability(), copy=False
    )
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', copy=False, readonly=True)
    bedrooms = fields.Integer('Bedrooms', default=2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area (sqm)')
    garden_orientation = fields.Selection(selection='_selection_garden_orientation', string='Garden Orientation')

    state = fields.Selection(selection='_selection_state', string='Status', required=True, copy=False, default='new')
    active = fields.Boolean('Active', default=True)

    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    salesperson_id = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')

    best_price = fields.Float('Best Offer', compute='_compute_best_price', help='Best offer received')
    total_area = fields.Integer(
        'Total Area (sqm)',
        compute='_compute_total_area',
        help='Total area computed by summing the living area and the garden area',
    )

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for prop in self:
            prop.best_price = max(prop.offer_ids.mapped('price')) if prop.offer_ids else 0.0

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for prop in self:
            prop.total_area = prop.living_area + prop.garden_area

    @api.model
    def _selection_garden_orientation(self):
        return [
            ('N', 'North'),
            ('S', 'South'),
            ('E', 'East'),
            ('W', 'West'),
        ]

    @api.model
    def _selection_state(self):
        return [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ]

    @api.constrains('expected_price', 'selling_price')
    def _check_selling_price(self):
        for record in self:
            if (
                    not float_is_zero(record.selling_price, precision_digits=2)
                    and float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) < 0
            ):
                raise ValidationError('The selling price cannot be lower than 90% of the expected price.')

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'N'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        if not set(self.mapped('state')) <= {'new', 'canceled'}:
            raise UserError('Only new and canceled properties can be deleted.')

    def action_cancel(self):
        self.ensure_one()

        if self.state == 'sold':
            raise UserError('Sold properties cannot be canceled.')

        return self.write({'state': 'canceled'})

    def action_sell(self):
        self.ensure_one()

        if self.state == 'canceled':
            raise UserError('Canceled properties cannot be sold.')
        if not any(offer.state == 'accepted' for offer in self.offer_ids):
            raise UserError("Cannot sell a property that doesn't have an accepted offer.")

        return self.write({'state': 'sold'})
