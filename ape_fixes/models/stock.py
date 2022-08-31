# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    final_weight = fields.Float(string='Shipping Weight',digits='Stock Weight',help="Total weight of the products in the picking.")


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