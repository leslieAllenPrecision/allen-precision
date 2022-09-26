# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_number = fields.Char(related="partner_id.ref",string="Customer Number")
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="[('ref','!=',False),('customer_rank','>',0),'|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

    @api.model
    def create(self,vals):
        if vals.get('partner_id'):
            partner = self.env['res.partner'].sudo().browse(int(vals.get('partner_id')))
            if not partner.ref:
                raise UserError('Cannot create sale order for customer not having customer number')
        res = super(SaleOrder,self).create(vals)
        return res


