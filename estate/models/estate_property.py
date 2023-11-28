from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils
from datetime import date
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real estate properties'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'),
                   ('sold', 'Sold'), ('canceled', 'Canceled')], required=True, copy=False, default='new')
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=date.today() + relativedelta(months=+3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    best_price = fields.Float(compute='_compute_best_price')
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    total_area = fields.Integer(compute='_compute_total_area')

    property_type_id = fields.Many2one('estate.property.type')
    buyer_id = fields.Many2one('res.partner', copy=False)
    salesperson_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag')
    offer_ids = fields.One2many('estate.property.offer', 'property_id')

    _sql_constraints = [('check_property_expected_price', 'CHECK ( expected_price > 0 )',
                         'The expected price must be strictly positive'), (
                        'check_property_selling_price', 'CHECK ( selling_price >= 0 )',
                        'The selling price must be positive')]

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped('price') + [0])

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    @api.ondelete(at_uninstall=False)
    def _unlink_if_state_new_or_canceled(self):
        if any(record.state not in ['new', 'canceled'] for record in self):
            raise UserError('Can only delete new or canceled property')

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if (float_utils.float_compare(record.selling_price, 0.9 * record.expected_price, precision_digits=2) < 0 and
                    not float_utils.float_is_zero(record.selling_price, precision_digits=2)):
                raise ValidationError('The selling price cannot be lower than 90% of the expected price')

    def cancel_property(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('Sold properties cannot be canceled')
            else:
                record.state = 'canceled'
        return True

    def sell_property(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError('Canceled properties cannot be sold')
            else:
                record.state = 'sold'
        return True
