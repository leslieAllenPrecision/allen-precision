# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale

import logging
_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update/multi/variant'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_multi_variant(self, data, **post):
        if data:
            for i in range(len(data)):
                self.cart_update(
                    product_id=data[i]['product_id'],
                    add_qty=data[i]['add_qty'],
                )
            if post.get('express'):
                return {'redirect_url': '/shop/checkout?express=1'}
            return {'redirect_url': '/shop/cart'}
        else:
            return False
