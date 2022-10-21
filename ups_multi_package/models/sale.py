# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_package_ids = fields.One2many('delivery.package','order_id')