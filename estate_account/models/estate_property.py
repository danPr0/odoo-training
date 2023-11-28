from odoo import models, Command


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def sell_property(self):
        if super().sell_property():
            for record in self:
                self.env['account.move'].create(
                    {
                        'partner_id': record.buyer_id.id,
                        'move_type': 'out_invoice',
                        'invoice_line_ids': [
                            Command.create({
                                'name': '6% of the selling price',
                                'quantity': 1.0,
                                'price_unit': 0.06 * record.selling_price
                            }),
                            Command.create({
                                'name': 'An additional 100.00 from administrative fees',
                                'quantity': 1.0,
                                'price_unit': 100.00
                            })
                        ]
                    })
            return True
        else:
            return False
