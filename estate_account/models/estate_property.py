from odoo import models, Command


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sell(self):
        if super().action_sell() and self.check_access_rights('write') and self.check_access_rule('write'):
            for record in self:
                self.env['account.move'].sudo().create(
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
