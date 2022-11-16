# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class DeliveryPackage(models.Model):
    _name = "delivery.package"
    _description = "This Module manage the multiple packages for delivery"

    height = fields.Float(string='Height')
    width = fields.Float(string='width')
    length = fields.Float(string='length')
    weight = fields.Float(string='weight')
    order_id = fields.Many2one('sale.order',string='Order id')
    picking_id = fields.Many2one('stock.picking',string='Picking Id')
