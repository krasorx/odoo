from email.policy import default
from odoo import api,models, fields
from num2words import num2words
import datetime

class estate_property(models.Model):
    _name = "property.lote"
    _description = "un modelo de prueba"

    _sql_constraints = [
        ('unique_property_lote', 'unique (lote)',     
                 'No se permiten lotes duplicados')]

    name = fields.Char(string="Area", default="Backroom 1", required=True)
    description = fields.Text(string="Descripcion", default="Una descripcion")
    lote = fields.Char(string="Lote", default="0")
    barrio = fields.Char(string="Barrio", default="Barrio 1")
    postcode = fields.Char(string="Codigo Postal")
    active = fields.Boolean(string="Activo", default=True)
    date_availability = fields.Date(string="Disponible desde", default=lambda self: (fields.Datetime.now() + datetime.timedelta(days=90)))
    last_seen = fields.Datetime(string="Ultima vez vista",default=lambda self: fields.Datetime.now(),readonly=True)
    expected_price = fields.Float(string="Precio esperado(USD)",required=True, default=10.0)
    selling_price = fields.Float(string="Precio de venta(USD)",readonly=True)
    living_area = fields.Float(string="Area(m²)",default=100)
    garden_area = fields.Integer(string="Area del jardin(m²)", default=0.0)
    state = fields.Selection(string='Estado', 
                            selection=[
                                ('nuevo', 'NUEVO'), 
                                ('oferta recibida','Oferta Recibida'),
                                ('reserva aceptada', 'Recerva Aceptada'),
                                ('vendido', 'Vendido'), 
                                ('reservado','RESERVADO'),
                                ('cancelado','Cancelado')],
                            default='nuevo' ,help="New Offer Recieved Offer Accepted Sold and Cancelled")
    property_type_id = fields.Many2one("property.type", string="Tipo")
    sales_person_id = fields.Many2one('res.users', string='Vendedor', index=True, 
                                tracking=True, default=lambda self: self.env.user)
    tag_ids = fields.Many2many("property.tag", string="Tags")
    buyer_id = fields.Many2one('res.partner', string='Comprador')
    offer_ids = fields.One2many("property.offer","property_id" ,string="Ofertas")
    total_area = fields.Float(string="Area total (m²)", compute="_compute_total_area")
    best_price = fields.Float(string="Mejor precio", compute="_compute_best_price", default=0.0)
    expresed_value = fields.Char(string="Valor expresado", compute="_compute_expresed_value",
                                default="VEINTE MIL DOLARES ESTADOUNIDENSES" )

    price_reserve = fields.Float(string="Anticipo", compute="_compute_price_reserve", readonly=True )
    price_reinforment_m9 = fields.Float(string="Refuerzo mes 9", compute="_compute_reinforment_m9", readonly=True)
    price_reinforment_m18 = fields.Float(string="Refuerzo mes 18", compute="_compute_reinforment_m18", readonly=True)
    price_balance = fields.Float(string="Saldo", compute="_compute_balance", readonly=True)
    price_balance_usd = fields.Float(string="Saldo en USD", compute="_compute_balance_usd", readonly=True)
    price_balance_pesos_cac = fields.Float(string="Saldo en pesos mas CAC", compute="_compute_balance_pesos_cac", readonly=True)
    price_discount_55_reserve = fields.Float(string="Descuento del 10 abonando 55 de anticipo", compute="_compute_discount_55_reserve", readonly=True)
    price_discount_one_payment = fields.Float(string="Descuento del 15 pago contado", compute="_compute_discount_one_payment", readonly=True)
    cuotas = fields.Integer(string="Cuotas", default=30)

    @api.depends("expected_price", "price_reserve")
    def _compute_price_reserve(self):
        for record in self:
            record.price_reserve = record.expected_price * 0.35

    @api.depends("expected_price", "price_reinforment_m9")
    def _compute_reinforment_m9(self):
        for record in self:
            record.price_reinforment_m9 = record.expected_price * 0.10
    

    @api.depends("expected_price", "price_reinforment_m18")
    def _compute_reinforment_m18(self):
        for record in self:
            record.price_reinforment_m18 = record.expected_price * 0.10

    @api.depends("expected_price", "price_balance")
    def _compute_balance(self):
        for record in self:
            record.price_balance = record.expected_price * 0.45

    @api.depends("price_balance", "price_balance_usd")
    def _compute_balance_usd(self):
        for record in self:
            record.price_balance_usd = record.price_balance / 36

    @api.depends("price_balance_usd", "price_balance_pesos_cac")
    def _compute_balance_pesos_cac(self):
        for record in self:
            record.price_balance_pesos_cac = record.price_balance_usd * 200

    @api.depends("expected_price", "price_discount_55_reserve")
    def _compute_discount_55_reserve(self):
        for record in self:
            record.price_discount_55_reserve = record.expected_price * 0.9
    
    @api.depends("expected_price", "price_discount_one_payment")
    def _compute_discount_one_payment(self):
        for record in self:
            record.price_discount_one_payment = record.expected_price * 0.85
    
    # para ampliar en un futuro, si nos dan varias areas distintas para un mismo lote
    @api.depends("living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area

    @api.depends("offer_ids","best_price")
    def _compute_best_price(self):
        for record in self:
            if(record.offer_ids):
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0.0
    
    @api.depends("expected_price", "expresed_value")
    def _compute_expresed_value(self):
        for record in self:
            record.expresed_value = num2words(record.expected_price, lang='es').upper() + " DOLARES ESTADOUNIDENSES"

    def action_sell(self):
        for record in self:
            if(record.state != 'cancelado'):
                record.state = "vendido"
                record.selling_price = record.best_price
        return True

    def action_cancel(self):
        for record in self:
            if(record.state != 'vendido'):
                record.state = "cancelado"
        return True
    
    def action_reserve(self):
        for record in self:
            if(record.state != 'vendido' & record.state != 'cancelado'):
                record.state = "RESERVADO"
        return True

    def action_reserve2(self):
        for record in self:
            #TODO Check if the property is avaible and if it is
            #procede with the reserve
            record.state = "reservado"
        return True

    def action_accepOffer(self):
        for record in self:
            record.state = "reserva aceptada"
        return True
        
    def action_generate_contract(self):
        for record in self:
            record.state = "vendido"
        return True

    @api.depends('name', 'barrio', 'lote')
    def name_get(self):
        res=[]
        for record in self:
            namae = record.barrio + " lote: "+ record.lote  
            res.append((record.id,namae  ))
        return res
    
    

    