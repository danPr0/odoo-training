from odoo import models


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def sell_property(self):
        # self.env['account.move'].create({'partner_id': self.salesperson_id, 'move_type': 'out_invoice'})
        if super().sell_property():
            pass
            return True
        else:
            return False
