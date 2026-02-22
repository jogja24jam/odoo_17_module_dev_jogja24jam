from odoo import fields, models
from odoo.exceptions import ValidationError

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'A property type name must be unique.'),
    ]

    name = fields.Char(required=True)
    