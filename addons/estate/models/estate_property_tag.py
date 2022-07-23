from odoo import api,models, fields

class estate_property_tag(models.Model):
    _name = "property.tag"
    _description = "Tag para agregar a una propiedad"

    name = fields.Char(string="Tag",required=True, default="habitable")
    