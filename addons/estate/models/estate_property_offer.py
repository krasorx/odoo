from odoo import api, http,models, fields
from num2words import num2words
import datetime

class partner_inherit(models.Model):
    _inherit= 'res.partner'

    cuil = fields.Char(string="Cuit/Cuil")
    dni = fields.Char(string="D.N.I", size=8)

class estate_property_offer(models.Model):
    _name = "property.offer"
    _description = "una oferta de compra a una propiedad."

    _sql_constraints = [
        ('unique_property_ids', 'unique (property_id)',     
                 'No se permiten duplicados')]

    archival_info = fields.Text(string="Información de la reserva, en caso de cancelacion")
    price = fields.Float(string="Valor de anticipo(usd)" , default=1000.0)
    price_final = fields.Float(string="Precio Final(usd)", compute="_compute_price_final")
    price_final_expresed_value = fields.Char(string="Precio final expresado(USD)", compute="_compute_price_final_expresed_value",
                                default="VEINTE MIL DOLARES ESTADOUNIDENSES" )
    status = fields.Selection(
        string='Estado', selection=[('refused', 'Refused'), 
        ('accepted', 'Accepted'), 
        ('pendiente', 'Pendiente'),
        ('expirado', 'Expirado')], help="Rechazado, Aceptado, pendiente o expirado",
        default='pendiente')
    validity_days = fields.Integer(string="Validez(días)", default=2, readonly=True)
    date_deadline = fields.Datetime(string="Fecha limite", compute="_compute_validity_days",
                            inverse="_inverse_validity_days", store=True)
    marital_status = fields.Selection(
        string='Estado', selection=[('soltero', 'Soltero'), 
        ('casado', 'Casado')], help="Soltero o casado"
    )
    marital2_status = fields.Selection(
        string='Estado', selection=[('soltero', 'Soltero'), 
        ('casado', 'Casado')], help="Soltero o casado"
    )
    marital3_status = fields.Selection(
        string='Estado', selection=[('soltero', 'Soltero'), 
        ('casado', 'Casado')], help="Soltero o casado"
    )
    marital4_status = fields.Selection(
        string='Estado', selection=[('soltero', 'Soltero'), 
        ('casado', 'Casado')], help="Soltero o casado"
    )
    date_of_reserve = fields.Datetime(string="Fecha de reserva",default=fields.Datetime.now() )
    create_date = fields.Datetime(string="Fecha de creación", readonly=True)
    payment_method = fields.Selection(
        string='Forma de pago', selection=[
        ('contado', 'Contado'), 
        ('55', '55% anticipo + refuerzos + cuotas'),
        ('35', '35% de anticipo + refuerzos + cuotas'),
        ('otra', 'Otra'), 
        ],
        default='contado' ,help="Seleccionar el tipo de pago")
    other_payment_method = fields.Text(string="Otro metodo de pago")
    cuotas_amount = fields.Integer(string="Cantidad de cuotas", default=30)

    partner_id = fields.Many2one('res.partner', string='Titular 1')
    partner1_id = fields.Many2one('res.partner', string='Pareja Titular 1')
    partner2_id = fields.Many2one('res.partner', string='Titular 2')
    partner3_id = fields.Many2one('res.partner', string='Pareja Titular 2')
    property_id = fields.Many2one('property.lote', string='Unidad Funcional')
    partner4_id = fields.Many2one('res.partner', string='Titular 3')
    partner5_id = fields.Many2one('res.partner', string='Pareja Titular 3')
    partner6_id = fields.Many2one('res.partner', string='Titular 4')
    partner7_id = fields.Many2one('res.partner', string='Pareja Titular 4')
    is_new = fields.Boolean(default=True, copy=False)
    sales_person_id = fields.Many2one('res.users', string='Inmobiliaria', index=True, 
                                tracking=True, default=lambda self: self.env.user)
    offer_number = fields.Char(string="Número de reserva",readonly=True ,index=True, copy=False)
    reserve_amount_percent = fields.Float(string="Porcentaje anticipo", compute="_compute_reserve_amount_percent", readonly=True )
    property_barrio = fields.Char(related="property_id.barrio", string="Proyecto", default="backroom", store=True)
    property_lote = fields.Char(related="property_id.lote", string="Lote", store=True)
    property_description = fields.Text(related="property_id.description", string="Descripcion", store=True)
    property_state = fields.Selection(
        string='Estado', related="property_id.state", store=True, copy=False)
    property_expresed_value = fields.Char(related="property_id.expresed_value",string="Precio total(USD)",required=True,readonly=True)
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
    
    property_price_reinforment_m9_expresed_value = fields.Char(string="Refuerzo mes 9(USD)",readonly=True)

    state = fields.Selection(selection=[
       ('reserva', 'Reserva'),
       ('modo de pago', 'Modo de pago'),
       ('contrato', 'Contrato'),
       ('cancelar', 'Cancelado'),
       ('hecho', 'Hecho'),
   ], string='Estado', required=True, readonly=True, copy=False,
   tracking=True, default="reserva")
    #datos para generar contrato
    price_total_1 = fields.Float(string="precio 1")
    price_reserve_1 = fields.Float(string="precio 1")

    cbu_dolars_number = fields.Char(string="Cuenta Corriente Especial en Dólares N°")
    cbu_pesos_number = fields.Char(string="Cuenta Corriente en Pesos N°")
    cbu_dolars = fields.Char(string="CBU Cuenta Corriente Especial en Dólares")
    cbu_pesos = fields.Char(string="CBU Cuenta Corriente en Pesos")

    #@api.constrains('property_id')
    #def _check_property_unique(self):
    #    for record in self:
    #        if record.property_id == record:
    #            raise ValidationError("The end date cannot be set in the past")

    @api.model
    def create(self, vals): 
        vals['offer_number'] = self.env['ir.sequence'].next_by_code('property.offer')
        obj = super(estate_property_offer, self).create(vals)
        #number = self.env['ir.sequence'].next_by_code('property.offer.sequence')
        #print('numero:',number)
        #obj.write({'offer_number': number})
        return obj

    @api.depends("validity_days", "is_new")
    def _compute_validity_days(self):
        for record in self:
            if(record.is_new):
                record.is_new = False
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
                   #envia un email a la desarrolladora
            print("deberia enviar un email")
            mail_template = self.env.ref('estate.template_email_reserve')
            email_to = 'luisesp27@live.com.ar'
            subject = 'Reserva de terreno ' + self.offer_number
            report_name = 'Contrato de Rerserva ' + self.offer_number
            body = ('Aviso de reserva de propiedad con lote: ' + self.property_lote + 
                    ' con número de reserva ' + self.offer_number + '. Para Confirmar o Denegar la reserva' 
                    + ' ingrese a este enlace: ' + str(http.request.env['ir.config_parameter'].get_param('web.base.url')) 
                    + str(http.request.httprequest.full_path) +
                    '. Esperando confirmación.')
            email_values = {
            'email_cc': False,
            'auto_delete': False,
            'email_to' : email_to,
            'subject': subject,
            'body_html': body,
            }   
            mail_template.send_mail(self.sales_person_id.id, force_send=True,email_values=email_values)
            print('url:',http.request.env['ir.config_parameter'].get_param('web.base.url') )
            print('URL: ',http.request.httprequest.full_path)

    def _inverse_validity_days(self):
        for record in self:
            if(record.is_new):
                record.is_new = False;
                record.validity_days = (
                    (record.date_deadline.toordinal() - fields.Datetime.now().toordinal())
                )
            else:
                days = (
                    (record.date_deadline.toordinal() - record.create_date.toordinal())
                )
                print(record.date_deadline.toordinal())
                record.validity_days = days


    #@api.depends("offer_number", "property_id")
    #def _compute_reserve_number(self):
    #    for record in self:
    #        record.offer_number = 501
    
    # calculates de % of the total price that the customer pays with the reserve
    @api.depends("reserve_amount_percent","property_expected_price", "price")
    def _compute_reserve_amount_percent(self):
        for record in self:
            record.reserve_amount_percent = (
                record.price * (100/record.property_expected_price)
                )

    
    @api.depends("price", "price_final", "property_expected_price")
    def _compute_price_final(self):
        for record in self:
            record.price_final = record.property_expected_price - record.price

    @api.depends("price_final", "price_final_expresed_value")
    def _compute_price_final_expresed_value(self):
        for record in self:
            record.price_final_expresed_value = num2words(record.price_final, lang='es').upper()

    def get_payment_date(self,aDate, daysToAdd):
        delta = datetime.timedelta(days=daysToAdd)
        return (aDate + delta)
    
    def get_expresed_value(self,aPrice):
        return (num2words(aPrice, lang='es').upper())

    def cancel_reserve(self):
        if((self.status == 'pendiente')):
            print("Borro la reserva")
            self.write({'status': "refused"   })
            self.write({'state': "cancelar"   })
            self.archival_info = "barrio: "   + self.property_barrio + " lote: " + self.property_lote
            self.property_id.action_cancel()
            self.property_id = None

    def button_payment_method(self):
        self.write({'state': "modo de pago"   })
 

    def button_cancel_reserve_method(self):
        self.write({'property_state': "nuevo"   })
    
    def button_accept_offer(self):
        self.write({'status': "accepted"   })
        if(self.state == 'modo de pago'):
            self.write({'state': "contrato"   })
            self.property_id.action_accepOffer()
        else:
            self.write({'state': "modo de pago"   })
        self.property_id.action_accepOffer()

    def button_cancel_offer(self):
        self.cancel_reserve()
    
    def button_save_reserve(self):
        print("un contrato")
    
    def button_contract(self):
        self.write({'state': "contrato"   })
        self.property_id.action_accepOffer()
        print(self.get_payment_date(self.date_of_reserve,275))

    @api.model
    def update_state_reserve(self):
        print("Se ejecuto el timer")
        
        offers = self.env['property.offer'].search([])
        for offer in offers:
            # if offer date deadline < today then it liberates the property to get a new offer
            if(offer.date_deadline < datetime.datetime.now()):
                offer.cancel_reserve()
            