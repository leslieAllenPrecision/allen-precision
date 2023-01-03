# -*- coding: utf-8 -*-

from optparse import Values
from signal import valid_signals
from odoo import models, fields, api ,_
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit='product.template'

    @api.constrains('default_code')
    def _check_default_code(self):
        for rec in self:
            if rec.default_code:
                p_id = rec.search([('default_code','=',rec.default_code),('id','not in',[rec.id])])
                if p_id:
                    raise  UserError(_(f'Internal Reference {rec.default_code} already exist in product {p_id.display_name}'))

  


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        name = self.display_name
        if self.description_sale:
            name = self.description_sale if not self.default_code else f'[{self.default_code}] {self.description_sale}'

        return name
    

    @api.constrains('default_code')
    def _check_default_code(self):
        for rec in self:
            if rec.default_code:
                p_id = rec.search([('default_code','=',rec.default_code),('id','not in',[rec.id])])
                if p_id:
                    raise  UserError(_(f'Internal Reference {rec.default_code} already exist in product {p_id.display_name}'))

    @api.model
    def create(self, vals):
        if not vals.get('default_code'):
            seq_date = None
            prefix = ''
            if vals.get('categ_id'):
                categ_id = self.env['product.category'].sudo().browse([int(vals.get('categ_id'))])
                if categ_id.product_prefix:
                    prefix=categ_id.product_prefix
            vals['default_code'] =f"{prefix}{self.env['ir.sequence'].next_by_code('product.template', sequence_date=seq_date) or _('New')}" 
        return super(ProductProduct,self).create(vals)




class ProductCategory(models.Model):
    _inherit='product.category'

    product_prefix =  fields.Char(string='Product Reference Prefix')
