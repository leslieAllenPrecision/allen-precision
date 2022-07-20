# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pre_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Default payment term',
        config_parameter='customer_approval.pre_payment_term_id',
        help="Payment terms which need to set by default in customers"
    )