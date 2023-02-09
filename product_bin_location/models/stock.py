# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # @api.model
    # def default_get(self, fields):
    #     vals = super(StockQuant, self).default_get(fields)
    #     product_template_id = False
    #     if self.env.context.get('active_model') == 'product.product':
    #         product_id = self.env['product.product'].browse(self.env.context.get('active_id'))
    #         product_template_id = product_id.product_tmpl_id
    #         # domain.insert(0, "('product_id', '=', %s)" % self.env.context.get('active_id'))
    #     elif self.env.context.get('active_model') == 'product.template':
    #         product_template_id = self.env['product.template'].browse(self.env.context.get('active_id'))
    #
    #     if product_template_id and product_template_id.bin_location_id:
    #         vals['location_id'] = product_template_id.bin_location_id.id
    #     return vals

