from odoo import Command, models

class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):

        result = super().action_sold()

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.buyer_id.id,
            'invoice_line_ids': [
                Command.create({
                    'name': 'Selling Price Commission',
                    'quantity': 1,
                    'price_unit': self.selling_price * 0.06,
                }),
                Command.create({
                    'name': 'Administration Fee',
                    'quantity': 1,
                    'price_unit': 100.00    ,
                }),
            ]
        }
        self.env['account.move'].create(invoice_vals)
        return result