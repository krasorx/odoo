from odoo import api,models, fields
import datetime

class estate_property_offer(models.Model):
    _name = "property.offer"
    _description = "una oferta de compra a una propiedad."

    price = fields.Float(string="Valor de anticipo(usd)" , default=1000.0)
    status = fields.Selection(
        string='Estado', selection=[('refused', 'Refused'), 
        ('accepted', 'Accepted'), ('pendiente', 'Pendiente')], help="Rechazado, Aceptado o pendiente",
        default='pendiente')
    validity_days = fields.Integer(string="Validez(días)", default=7)
    date_deadline = fields.Datetime(string="Fecha limite", compute="_compute_validity_days",
                            inverse="_inverse_validity_days")
    marital_status = fields.Selection(
        string='Estado', selection=[('soltero', 'Soltero'), 
        ('casado', 'Casado')], help="Soltero o casado"
    )
    marital2_status = fields.Selection(
        string='Estado', selection=[('soltero', 'Soltero'), 
        ('casado', 'Casado')], help="Soltero o casado"
    )
    date_of_reserve = fields.Date(string="Fecha de reserva",default=fields.Datetime.now() )
    payment_method = fields.Selection(
        string='Forma de pago', selection=[
        ('contado', 'Contado'), 
        ('55 de anticipo + refuerzos + cuotas', '55 porciento anticipo + refuerzos + cuotas'),
        ('35 de anticipo + refuerzos + cuotas', '35 porciento de anticipo + refuerzos + cuotas'),
        ('otra', 'Otra'), 
        ],
        default='contado' ,help="Seleccionar el tipo de pago")
    other_payment_method = fields.Text(string="Otro metodo de pago")

    partner_id = fields.Many2one('res.partner', string='Comprador1')
    partner1_id = fields.Many2one('res.partner', string='Pareja Comprador1')
    partner2_id = fields.Many2one('res.partner', string='Comprador2')
    partner3_id = fields.Many2one('res.partner', string='Pareja comprador2')
    property_id = fields.Many2one('test.model', string='Propiedad')
    payment_id = fields.Many2one('property.payment', string='Pago')
    is_new = fields.Boolean(default=True)
    sales_person_id = fields.Many2one('res.users', string='Inmobiliaria', index=True, 
                                tracking=True, default=lambda self: self.env.user)
    offer_number = fields.Integer(string="Número de reserva", compute="_compute_reserve_number")
    reserve_amount_percent = fields.Float(string="Porcentaje anticipo", compute="_compute_reserve_amount_percent", readonly=True )
    property_barrio = fields.Char(related="property_id.barrio", string="Barrio", default="backroom", store=True)
    property_lote = fields.Char(related="property_id.lote", string="Lote", store=True)
    property_description = fields.Text(related="property_id.description", string="Descripcion", store=True)
    property_state = fields.Selection(
        string='Estado', related="property_id.state", store=True
        ,selection=[('nuevo', 'NUEVO'), ('offer recieved','Offer Recieved'),('offer accepted', 'Offer Accepted'),
         ('sold', 'Sold'), ('reservado','RESERVADO'),('canceled','Canceled')] ,help="New Offer Recieved Offer Accepted Sold and Cancelled")
    property_total_area = fields.Float(related="property_id.total_area", string="Área(m²)", store=True)
    property_expected_price = fields.Float(related="property_id.expected_price",string="Precio total(USD)",required=True)
    property_price_reserve = fields.Float(related="property_id.price_reserve",string="Anticipo",readonly=True )
    property_price_reinforment_m9 = fields.Float(related="property_id.price_reinforment_m9",string="Refuerzo mes 9",readonly=True)
    property_price_reinforment_m18 = fields.Float(related="property_id.price_reinforment_m18",string="Refuerzo mes 18", readonly=True)
    property_price_balance = fields.Float(related="property_id.price_balance",string="Saldo", readonly=True)
    property_price_balance_usd = fields.Float(related="property_id.price_balance_usd",string="Saldo en USD", readonly=True)
    property_price_balance_pesos_cac = fields.Float(related="property_id.price_balance_pesos_cac",string="Saldo en pesos mas CAC", readonly=True)
    property_price_discount_55_reserve = fields.Float(related="property_id.price_discount_55_reserve",string="Descuento del 10 abonando 55 de anticipo", readonly=True)
    property_price_discount_one_payment = fields.Float(related="property_id.price_discount_one_payment",string="Descuento del 15 pago contado", readonly=True)
    
    state = fields.Selection(selection=[
       ('reserva', 'Reserva'),
       ('modo de pago', 'Modo de pago'),
       ('contrato', 'Contrato'),
       ('cancelar', 'Cancelado'),
       ('hecho', 'Hecho'),
   ], string='Estado', required=True, readonly=True, copy=False,
   tracking=True, default="reserva")

    @api.depends("validity_days", "is_new")
    def _compute_validity_days(self):
        for record in self:
            if(record.is_new):
                is_new = False
                record.date_deadline = (
                    (fields.Datetime.now() + datetime.timedelta(days=record.validity_days))
                )
            else:
                record.date_deadline = (
                    (record.create_date + datetime.timedelta(days=record.validity_days))
                )
    
    def button_reserve_method(self):
        if(((self.property_state != 'NUEVO') | (self.property_state != 'canceled'))):
            self.property_id.action_reserve2()
            self.write({'state': "modo de pago"   })

    def _inverse_validity_days(self):
        for record in self:
            record.validity_days = (
                (record.date_deadline.day - record.create_date.day)
            )
    @api.depends("offer_number", "property_id")
    def _compute_reserve_number(self):
        for record in self:
            record.offer_number = 501
    
    # calculates de % of the total price that the customer pays with the reserve
    @api.depends("reserve_amount_percent","property_expected_price", "price")
    def _compute_reserve_amount_percent(self):
        for record in self:
            record.reserve_amount_percent = (
                record.price * (100/record.property_expected_price)
                )

    def button_payment_method(self):
        self.write({'state': "modo de pago"   })

    def button_cancel_reserve_method(self):
        self.write({'property_state': "nuevo"   })
    
    def button_accept_offer(self):
        self.write({'status': "accepted"   })
        self.write({'state': "modo de pago"   })
        self.property_id.action_accepOffer()

    def button_cancel_offer(self):
        self.write({'status': "refused"   })
        self.write({'state': "cancelar"   })
        self.property_id.action_cancel()
    
    def button_save_reserve(self):
        print("un contrato")
    