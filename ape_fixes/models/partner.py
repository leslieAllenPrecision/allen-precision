# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_
import logging
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"



    @api.constrains('ref')
    def _check_ref(self):
        for rec in self:
            if rec.ref:
                p_id = rec.search([('ref','=',rec.ref),('id','not in',[rec.id])])
                if p_id:
                    raise  UserError(_(f'Customer Number {rec.ref} already exist in partner {p_id[0].name}'))

    @api.model
    def create(self, vals):
        res = super(ResPartner,self).create(vals)
        if not res.ref:
            seq_date = None
            prefix = ''
            if res.customer_rank and res.customer_rank > 0 and not res.parent_id:
                prefix='C'
                res.contact_type = 'cust'
                res.ref =f"{prefix}{self.env['ir.sequence'].next_by_code('res.partner.customer', sequence_date=seq_date) or _('New')}" 
            elif res.supplier_rank and res.supplier_rank > 0 and not res.parent_id:
                prefix = 'V'
                res.contact_type = 'ven'
                res.ref =f"{prefix}{self.env['ir.sequence'].next_by_code('res.partner.vendor', sequence_date=seq_date) or _('New')}" 
            else: 
                if res.contact_type == 'cust':
                    res.customer_rank = 1
                    prefix='C'
                    res.ref =f"{prefix}{self.env['ir.sequence'].next_by_code('res.partner.customer', sequence_date=seq_date) or _('New')}" 
                else:
                    res.supplier_rank = 1
                    prefix = 'V'
                    res.ref =f"{prefix}{self.env['ir.sequence'].next_by_code('res.partner.vendor', sequence_date=seq_date) or _('New')}" 

        return res




    customer_type = fields.Selection([('Regular','Regular'),('Resale','Resale'),('Government','Government'),('School','School'),('PLS/ENG','PLS/ENG'),('Construction','Construction'),('Other','Other'),('VENDOR','VENDOR')],string='Customer Type')
    contact_1 = fields.Char(string='Contact 1')
    contact_2 = fields.Char(string='Contact 2')
    contact_type = fields.Selection([('cust','Customer'),('ven','Vendor')],default='cust')
