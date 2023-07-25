# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends('line_ids.account_id.user_type_id.is_cogs_type',
                 'line_ids.account_id.user_type_id',
                 'line_ids.account_id',
                 'line_ids')
    def _get_cost_cogs(self):
        """
        Computes the Cost of Goods Sold (COGS) for each customer invoice and credit note.

        It computes the sum of the debit/credit amount for the move lines that belong to
        specific COGS accounts.

        :return: None
        """
        # Define mappings between move types and debit/credit amounts
        move_type_mappings = {'out_invoice': 'debit', 'out_refund': 'credit'}

        # Define the domain that will filter the accounts based on the user type's COGS flag
        cogs_accounts_domain = [('account_id.user_type_id.is_cogs_type', '=', True)]

        # Loop through each move in the recordset
        for move in self:
            # Determine the move type
            move_type = move.move_type

            # If the move type is a customer invoice or credit note
            if move_type in move_type_mappings.keys():
                # Get the sum of debit/credit amount for move lines that belong to COGS accounts
                cost_cogs = sum(move.line_ids.filtered_domain(cogs_accounts_domain).mapped(move_type_mappings[move_type])) or 0

                # COGS amount is negative for credit notes
                if move_type == 'out_refund':
                    cost_cogs = -abs(cost_cogs)

                # Store the COGS amount on the move record
                move.cost_cogs = cost_cogs
            else:
                move.cost_cogs = 0

    def _get_cost(self):
        """
        Computes the total cost of each move.

        It computes the sum of the cost field of move lines that belong to income accounts.

        :return: None
        """
        for move in self:
            # Get the sum of cost for move lines that belong to income accounts
            income_accounts = self.env['account.account'].search(
                [('internal_group', '=', 'income'), ('deprecated', '=', False)])
            move.cost_move_lines = sum(
                move.line_ids.filtered_domain([('account_id', 'in', income_accounts.ids)]).mapped('cost')) or 0

    def _get_cost_runtime(self):
        """
        Computes the runtime cost for each move.

        It computes the product of the standard_price and quantity fields of invoice line
        associated with each move.

        :return: None
        """
        for move in self:
            # Get the sum of the product of standard_price and quantity for invoice lines
            move.cost_runtime = sum([x.product_id.standard_price * x.quantity for x in move.invoice_line_ids]) or 0

    customer_number = fields.Char(string="Customer Number",store=True,compute="_get_customer_number")

    # TODO: These fields are only added to locate the issue reported in APE-12.
    #  Please remove them once the issue has been resolved.
    cost_runtime = fields.Float(compute='_get_cost_runtime', string='Cost Runtime')
    cost_cogs = fields.Float(compute='_get_cost_cogs', string="COGS", store=True)
    cost_move_lines = fields.Float(compute='_get_cost', string='Cost')

    @api.depends('partner_id')
    def _get_customer_number(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.parent_id:
                    rec.customer_number = rec.partner_id.parent_id.ref
                else:
                    rec.customer_number = rec.partner_id.ref
            else:
                rec.customer_number = False


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

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('product_id','quantity')
    def _calc_cost(self):
        for rec in self:
            if rec.product_id.rent_ok:
                rec.cost = 0.0
            else:
                rec.cost = rec.product_id.standard_price * rec.quantity

    @api.depends('account_id.user_type_id.is_cogs_type',
                 'account_id.user_type_id',
                 'account_id',
                 'product_id',
                 'move_id',
                 'move_id.move_type',
                 'move_id.line_ids',
                 'move_id.cost_cogs')
    def _get_cost_cogs(self):
        """
        Computes the Cost of Goods Sold (COGS) for each customer invoice and credit note.

        It computes the sum of the debit/credit amount for the move lines that belong to
        specific COGS accounts.

        :return: None
        """
        # Define mappings between move types and debit/credit amounts
        move_type_mappings = {'out_invoice': 'debit', 'out_refund': 'credit'}

        # Define the domain that will filter the accounts based on the user type's COGS flag
        cogs_accounts_domain = [('account_id.user_type_id.is_cogs_type', '=', True)]

        # Loop through each move in the recordset
        for line in self:
            line.cost_cogs = 0

            # If there are multiple lines for the same product, we only want to consider the first line.
            # We calculate the cost of goods sold (cost_cogs) for the first line, and for the remaining lines,
            # the cost_cogs will be set to zero.
            # This is done to ensure that the cost_cogs is calculated only once, even if we have multiple lines
            # for the same product.
            # This allows us to avoid double-counting when determining the price.

            same_product_lines = line.move_id.invoice_line_ids.filtered_domain(
                [('product_id', '=', line.product_id.id)])

            # If there are more than one line for the same product and at least one of them has a non-zero cost_cogs,
            # we skip further processing and move to the next line.
            if len(same_product_lines) > 1 and same_product_lines.filtered_domain([('cost_cogs', '!=', 0)]):
                continue

            # Determine the move type
            move = line.move_id
            move_type = line.move_id.move_type

            # If the move type is a customer invoice or credit note
            if move_type in move_type_mappings.keys():
                # Get the sum of debit/credit amount for move lines that belong to COGS accounts
                cost_cogs = sum(move.line_ids.filtered_domain(cogs_accounts_domain+[('product_id', '=', line.product_id.id)]).mapped(move_type_mappings[move_type])) or 0

                # COGS amount is negative for credit notes
                if move_type == 'out_refund':
                    cost_cogs = -abs(cost_cogs)

                # Store the COGS amount on the move record
                line.cost_cogs = cost_cogs
            else:
                line.cost_cogs = 0

    cost_cogs = fields.Float(compute='_get_cost_cogs', string="COGS", store='True')
    cost = fields.Float(string='Cost Price',compute='_calc_cost',store='True')


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    cost_cogs = fields.Float(string="COGS", readonly=True,)

    _depends = {
        'account.move.line': ['cost_cogs'],
    }

    def _select(self):
        return super()._select() + ",line.cost_cogs as cost_cogs"
