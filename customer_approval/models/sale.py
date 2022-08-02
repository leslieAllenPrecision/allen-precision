# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def action_confirm(self):
        self.ensure_one()  
        pre_payment_term_id =  self.env.company.pre_payment_term_id
        if pre_payment_term_id:
            if self.partner_id.property_payment_term_id.id != int(pre_payment_term_id) and not self.partner_id.is_approved:
                raise UserError("Customer is not approved, Kindly approve the customer to proceed further")
        return super(SaleOrder,self).action_confirm()
