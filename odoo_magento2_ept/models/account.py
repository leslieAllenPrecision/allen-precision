"""For Odoo Magento2 Connector Module"""
from odoo import models


class AccountTaxCode(models.Model):
    """Inherited account tax model to calculate tax."""
    _inherit = 'account.tax'

    def get_tax_from_rate(self, rate, name, is_tax_included=False):
        """
        This method,base on rate it find tax in odoo.
        @return : Tax_ids
        @author: Haresh Mori on dated 10-Dec-2018
        """
        for precision in [0.001, 0.01]:
            tax_ids = self.with_context(active_test=False).search(
                [('price_include', '=', is_tax_included),
                 ('type_tax_use', 'in', ['sale']),
                 ('amount', '>=', rate - precision),
                 ('amount', '<=', rate + precision), ('name', '=', name)], limit=1)
            if tax_ids:
                return tax_ids
        return self
