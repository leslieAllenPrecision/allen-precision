# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    customer_number = fields.Char(related="partner_id.ref",string='Customer Number')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res["invoice_date"] = datetime.now().date()
        return res



class ReportAccountAgedPartner(models.AbstractModel):   
    _inherit = "account.aged.partner"


    def _format_partner_id_line(self, res, value_dict, options):
        res['name'] = value_dict['partner_name'][:128] if value_dict['partner_name'] else _('Unknown Partner')
        if value_dict.get('partner_id',[]) and value_dict.get('partner_id',[])[0]:
            partner = self.env['res.partner'].browse(int(value_dict.get('partner_id',[])[0]))
            if partner.ref:
                res['name'] = res['name'] + f' ({partner.ref})'
        res['trust'] = value_dict['partner_trust']
 
