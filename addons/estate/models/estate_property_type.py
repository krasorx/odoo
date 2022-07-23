from odoo import api,models, fields

class estate_property_type(models.Model):
    _name = "property.type"
    _description = "tipo de propiedad"

    name = fields.Char(string="Tipo",required=True, default="Casa")