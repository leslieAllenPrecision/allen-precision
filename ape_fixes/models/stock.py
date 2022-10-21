# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    final_weight = fields.Float(string='Shipping Weight',digits='Stock Weight',help="Total weight of the products in the picking.")
    customer_number = fields.Char(string="Customer Number",store=True,compute="_get_customer_number")

    @api.depends('partner_id')
    def _get_customer_number(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.parent_id:
                    rec.customer_number = rec.partner_id.parent_id.ref
                else:
                    rec.customer_number = rec.partner_id.ref
            else:
                rec.customer_number = False

    @api.depends('move_line_ids.result_package_id', 'move_line_ids.result_package_id.shipping_weight', 'weight_bulk','final_weight')
    def _compute_shipping_weight(self):
        for picking in self:
            if picking.final_weight:
                picking.shipping_weight = picking.final_weight
            else:
                # if shipping weight is not assigned => default to calculated product weight
                picking.shipping_weight = picking.weight_bulk + sum([pack.shipping_weight or pack.weight for pack in picking.package_ids])


    @api.onchange('move_line_ids.result_package_id', 'move_line_ids.result_package_id.shipping_weight', 'weight_bulk')
    def on_shipping_weight(self):
        for picking in self:
            if not picking.final_weight:
                picking.shipping_weight = picking.weight_bulk + sum([pack.shipping_weight or pack.weight for pack in picking.package_ids])


class PackageType(models.Model):
    _inherit = 'stock.package.type'
    

    def _get_default_length_uom(self):
        return self.env.ref('uom.product_uom_inch').display_name


    def _compute_length_uom_name(self):
        for package_type in self:
            package_type.length_uom_name = self.env.ref('uom.product_uom_inch').display_name
