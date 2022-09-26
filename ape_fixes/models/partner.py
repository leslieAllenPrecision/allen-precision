# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_type = fields.Selection([('Regular','Regular'),('Resale','Resale'),('Government','Government'),('School','School'),('PLS/ENG','PLS/ENG'),('Construction','Construction'),('Other','Other'),('VENDOR','VENDOR')],string='Customer Type')
    contact_1 = fields.Char(string='Contact 1')
    contact_2 = fields.Char(string='Contact 2')
