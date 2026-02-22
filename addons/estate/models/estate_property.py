from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive.'),
    ]

    name = fields.Char("Title", required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date("Availability Date", copy=False, default=lambda self: fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer("Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        required=True,
        default='new',
        copy=False,
    )
    # Many2one setiap property memiliki satu type, satu salesman, dan satu buyer
    property_type_id = fields.Many2one('estate.property.type', string="Property Type")
    salesperson_id = fields.Many2one('res.users', string="Salesman", index=True, default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string="Buyer", index=True, copy=False)
    # Many2many setiap property memiliki banyak tag, dan setiap tag bisa untuk banyak property
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    # One2many setiap property memiliki banyak offer, tetapi setiap offer hanya untuk satu property
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")

    total_area = fields.Integer("Total Area (sqm)", compute="_compute_total_area")
    best_price = fields.Float("Best Offer", compute="_compute_best_price")


    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0.0

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue
            minimum_selling_price = record.expected_price * 0.9
            if float_compare(record.selling_price, minimum_selling_price, precision_digits=2) < 0:
                raise ValidationError(
                    _("The selling price cannot be lower than 90%% of the expected price.")
                )

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, precision_digits=2):
                if float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) < 0:
                    raise ValidationError(
                        _("The selling price cannot be lower than 90% of the expected price.")
                    )

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("Garden area set to 10 sqm and orientation set to North by default."),
                }
            }
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError(_("Canceled properties cannot be marked as sold."))
            record.state = 'sold'
        return True

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError(_("Sold properties cannot be canceled."))
            record.state = 'canceled'
        return True

    