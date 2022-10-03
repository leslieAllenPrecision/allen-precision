# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"


    bin_location_id = fields.Many2one('stock.location',string='Default Product Location')

# class StockQuant(models.Model):
#     _inherit = "stock.quant"

#     @api.model
#     def default_get(self, fields):
#         res = super().default_get(fields)
#         if 
#         res["invoice_date"] = datetime.now().date()
#         return reso