# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"
    

    is_approved = fields.Boolean(string='Is Customer Approved',default=False)

    approval_needed = fields.Boolean(string="Approval Needed",compute="_compute_approval_needed")

    def _compute_approval_needed(self):
        pre_payment_term_id =  self.env['ir.config_parameter'].get_param('customer_approval.pre_payment_term_id', False)
        for rec in self:
            if rec.is_approved or (pre_payment_term_id and  rec.property_payment_term_id.id == int(pre_payment_term_id)):
                rec.approval_needed = False
            else:
                rec.approval_needed = True
            

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        pre_payment_term_id =  self.env['ir.config_parameter'].get_param('customer_approval.pre_payment_term_id', False)
        if pre_payment_term_id:
            res["property_payment_term_id"] = int(pre_payment_term_id)
        return res

    def _approve_customer(self):
        self.is_approved = True
        self.message_post(body=("Customer Approved"))


    def button_approve(self):
        self._approve_customer()