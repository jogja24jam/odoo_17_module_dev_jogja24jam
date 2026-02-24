from odoo import fields, models
from odoo.exceptions import ValidationError

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _order = 'name'
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'A property tag name must be unique.'),
    ]

    name = fields.Char(required=True)
    color = fields.Integer()