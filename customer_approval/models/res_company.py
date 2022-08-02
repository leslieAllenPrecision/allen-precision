# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    pre_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Default payment term',
        help="Payment terms which need to set by default in customers"
    )