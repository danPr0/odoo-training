from odoo import models, Command


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sell(self):
        self.ensure_one()

        res = super().action_sell()
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        # Another way to get the journal:
        # journal = self.env["account.move"].with_context(default_move_type="out_invoice")._get_default_journal()

        if self.check_access_rights('write') and self.check_access_rule('write'):
            for prop in self:
                self.env['account.move'].sudo().create(
                    {
                        'partner_id': prop.buyer_id.id,
                        'move_type': 'out_invoice',
                        'journal_id': journal.id,
                        'invoice_line_ids': [
                            Command.create({
                                'name': prop.name,
                                'quantity': 1.0,
                                'price_unit': prop.selling_price * 0.06
                            }),
                            Command.create({
                                'name': 'Administrative fees',
                                'quantity': 1.0,
                                'price_unit': 100.00
                            })
                        ]
                    })
        return res
