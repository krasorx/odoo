from odoo import api,models, fields
import datetime

class estate_property_payment(models.Model):
    _name = "property.payment"
    _description = "Documento de pago."
    
    property_id = fields.Many2one('test.model', string='Propiedad')
    offer_ids = fields.One2many("property.offer","payment_id" ,string="Oferta")
    date_of_reserve = fields.Date(string="Fecha de reserva", readonly=True,default=fields.Datetime.now() )
    payment_method = fields.Selection(
        string='Forma de pago', selection=[
        ('contado', 'Contado'), 
        ('55 de anticipo + refuerzos + cuotas', '55 porciento anticipo + refuerzos + cuotas'),
        ('35 de anticipo + refuerzos + cuotas', '35 porciento de anticipo + refuerzos + cuotas'),
        ('otra', 'Otra'), 
        ],
        default='contado' ,help="Seleccionar el tipo de pago")