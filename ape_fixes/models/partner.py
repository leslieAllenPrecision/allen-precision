# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        res = super(ResPartner,self).create(vals)
        if not res.ref:
            seq_date = None
            prefix = ''
            if res.customer_rank and res.customer_rank > 0 and not res.parent_id:
                prefix='C'
                res.ref =f"{prefix}{self.env['ir.sequence'].next_by_code('res.partner.customer', sequence_date=seq_date) or _('New')}" 
            elif res.supplier_rank and res.supplier_rank > 0 and not res.parent_id:
                prefix = 'V'
                res.ref =f"{prefix}{self.env['ir.sequence'].next_by_code('res.partner.vendor', sequence_date=seq_date) or _('New')}" 
        return res




    customer_type = fields.Selection([('Regular','Regular'),('Resale','Resale'),('Government','Government'),('School','School'),('PLS/ENG','PLS/ENG'),('Construction','Construction'),('Other','Other'),('VENDOR','VENDOR')],string='Customer Type')
    contact_1 = fields.Char(string='Contact 1')
    contact_2 = fields.Char(string='Contact 2')
