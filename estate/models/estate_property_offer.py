from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'
    _order = 'price desc'
    _sql_constraints = [
        ('check_price', 'CHECK ( price > 0 )', 'The offer price must be strictly positive'),
    ]

    price = fields.Float('Price', required=True)
    validity = fields.Integer('Validity (days)', default=7)

    state = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        string='Status',
        copy=False,
    )

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    property_type_id = fields.Many2one(
        'estate.property.type', related='property_id.property_type_id', string='Property Type', store=True
    )

    date_deadline = fields.Date('Deadline', compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - date).days

    @api.model
    def create(self, vals):
        if vals.get("property_id") and vals.get("price"):
            prop = self.env["estate.property"].browse(vals["property_id"])
            if prop.state == 'sold':
                raise UserError('You cannot create an offer for a sold property')

            if prop.offer_ids:
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals["price"], max_offer, precision_digits=2) <= 0:
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "offer_received"

        return super().create(vals)

    def action_accept(self):
        if 'accepted' in self.mapped('property_id.offer_ids.state'):
            raise UserError('An offer has already been accepted.')
        self.write(
            {
                'state': 'accepted',
            }
        )
        return self.mapped('property_id').write(
            {
                'state': 'offer_accepted',
                'selling_price': self.price,
                'buyer_id': self.partner_id.id,
            }
        )

    def action_refuse(self):
        return self.write(
            {
                'state': 'refused'
            }
        )
