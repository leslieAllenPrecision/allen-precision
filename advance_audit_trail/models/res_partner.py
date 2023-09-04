# See LICENSE file for full copyright and licensing details.
"""Res Partner Model."""

from odoo import fields, models


class ResPartner(models.Model):
    """Res Partner Model."""

    _inherit = "res.partner"

    # Overridden below fields to fix the issues by adding
    # the base.group_partner_manager group.
    signup_token = fields.Char(
        copy=False, groups="base.group_erp_manager,base.group_partner_manager"
    )
    signup_type = fields.Char(
        string="Signup Token Type",
        copy=False,
        groups="base.group_erp_manager,base.group_partner_manager",
    )
    signup_expiration = fields.Datetime(
        copy=False, groups="base.group_erp_manager,base.group_partner_manager"
    )
