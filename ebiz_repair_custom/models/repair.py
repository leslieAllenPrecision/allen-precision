# -*- coding: utf-8 -*-

from odoo import fields, models


class Repair(models.Model):
    _inherit = 'repair.order'

    product_information = fields.Char()
