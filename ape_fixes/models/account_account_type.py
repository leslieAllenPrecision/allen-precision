# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountAccountType(models.Model):
    _inherit = 'account.account.type'

    is_cogs_type = fields.Boolean()