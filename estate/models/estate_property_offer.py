from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.tools import float_utils
from datetime import date
from dateutil.relativedelta import relativedelta


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate property offers'

    price = fields.Float()
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)

    _sql_constraints = [
        ('check_property_offer_price', 'CHECK ( price > 0 )', 'The offer price must be strictly positive')]

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date.date() + relativedelta(days=record.validity)
            else:
                record.date_deadline = date.today() + relativedelta(days=record.validity)

    @api.model
    def create(self, vals):
        estate_property = self.env['estate.property'].browse(vals['property_id'])
        if float_utils.float_compare(vals['price'], estate_property.best_price,
                                     precision_digits=2) < 0:
            raise UserError(f'The offer must be higher than {estate_property.best_price}')
        else:
            estate_property.state = 'offer_received'
            return super().create(vals)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - record.create_date.date()).days

    def accept_offer(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id

    def refuse_offer(self):
        for record in self:
            record.status = 'refused'
