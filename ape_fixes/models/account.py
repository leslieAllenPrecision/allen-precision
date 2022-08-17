# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res["invoice_date"] = datetime.now().date()
        return res
    