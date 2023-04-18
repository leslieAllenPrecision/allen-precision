# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"
    

    is_approved = fields.Boolean(string='Is Customer Approved',default=False)

    approval_needed = fields.Boolean(string="Approval Needed",compute="_compute_approval_needed")

    def write(self, vals):
        if self.env.user.has_group('customer_approval.group_hide_edit_ebiz'):
            return super(ResPartner, self.sudo()).write(vals)
        return super(ResPartner, self).write(vals)

    def _compute_approval_needed(self):
        for rec in self:
            pre_payment_term_id =  rec.company_id.pre_payment_term_id.id
            if rec.is_approved or (pre_payment_term_id and  rec.property_payment_term_id.id == int(pre_payment_term_id)):
                rec.approval_needed = False
            else:
                rec.approval_needed = True
            

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        pre_payment_term_id = False
        if self.env.company:
            pre_payment_term_id =  self.env.company.pre_payment_term_id.id
        if pre_payment_term_id:
            res["property_payment_term_id"] = int(pre_payment_term_id)
        return res

    def _approve_customer(self):
        self.is_approved = True
        self.message_post(body=("Customer Approved"))


    def button_approve(self):
        self._approve_customer()
