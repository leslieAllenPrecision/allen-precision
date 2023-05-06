odoo.define('website_grouped_product.ProductConfiguratorMixin', function (require) {
    'use strict';

    var core = require('web.core');
    var ajax = require('web.ajax');
    var config = require('web.config');
    var QWeb = core.qweb;
    var sAnimations = require('website.content.snippets.animation');
    var ProductConfiguratorMixin = require('website_sale_stock.VariantMixin');
    var StockProductConfiguratorMixin = require('website_sale_stock.VariantMixin');
    
    var xml_load = ajax.loadXML('/website_sale_stock/static/src/xml/website_sale_stock_product_availability.xml',QWeb);

    sAnimations.registry.GroupProductSale = sAnimations.Class.extend(ProductConfiguratorMixin, {
        selector: '.oe_website_sale',
        read_events: {
            'change form .js_product:not(:first) input[name="add_qty"]': '_onChangeAddGrpQuantity',
            'submit form.pro_combo': '_onSubmitCombo',
        },

        _onChangeAddGrpQuantity: function (ev) {
            this.onChangeAddQuantity(ev);
        },

        _onSubmitCombo: function (ev) {
            ev.preventDefault();
            return false;
        },

    });
    
    ProductConfiguratorMixin._onChangeCombinationGroup = function(ev, $parent, combination) {
        var $price = $parent.find(".oe_price:first .oe_currency_value");
        var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
        var $optional_price = $parent.find(".oe_optional:first .oe_currency_value");

        var isCombinationPossible = true;

        if (!_.isUndefined(combination.is_combination_possible)) {
            isCombinationPossible = combination.is_combination_possible;
        }

        this._toggleDisable($parent, isCombinationPossible);

        $price.html(ProductConfiguratorMixin._priceToStr(combination.price));
        $default_price.html(ProductConfiguratorMixin._priceToStr(combination.list_price));

        if (combination.has_discounted_price) {
            $default_price
                .closest('.oe_website_sale')
                .addClass("discount");
            $optional_price
                .closest('.oe_optional')
                .removeClass('d-none')
                .css('text-decoration', 'line-through');
            $default_price.parent().removeClass('d-none');
        } else {
            $default_price
                .closest('.oe_website_sale')
                .removeClass("discount");
            $optional_price.closest('.oe_optional').addClass('d-none');
            $default_price.parent().addClass('d-none');
        }

        var isMainProduct = combination.product_id &&
            ($parent.is('.js_main_product') || $parent.is('.main_product')) &&
            combination.product_id === parseInt($parent.find('.product_id').val());

        var isGroupChild = combination.product_id && ($parent.is('.p_variant'))

        if (isGroupChild){
            var qty = $parent.find('input[name="add_qty"]').val();
            
            $parent.parent().parent().next().next().find('#buy_now').removeClass('disabled out_of_stock');
            $parent.parent().parent().next().next().find('#add_to_cart').removeClass('disabled out_of_stock');

            if (combination.product_type === 'product' && _.contains(['always', 'threshold'], combination.inventory_availability)) {
                combination.virtual_available -= parseInt(combination.cart_qty);
                if (combination.virtual_available < 0) {
                    combination.virtual_available = 0;
                }
                // Handle case when manually write in input
                if (qty > combination.virtual_available) {
                    var $input_add_qty = $parent.find('input[name="add_qty"]');
                    qty = combination.virtual_available || 1;
                    $input_add_qty.val(qty);
                }
                if (qty > combination.virtual_available
                    || combination.virtual_available < 1 || qty < 1) {
                    $parent.find('#add_to_cart').addClass('disabled out_of_stock');
                    $parent.find('#buy_now').addClass('disabled out_of_stock');
                }
            }
            xml_load.then(function () {
                var $message = $(QWeb.render(
                'website_sale_stock.product_availability',
                combination
            ));
                $parent.find('div.availability_messages').html($message);
            });
        } else{
            return;
        }
    }

   
    sAnimations.registry.WebsiteSale.include({
        _onChangeCombination: function (ev, $parent, combination){
            if ($("div.p_variant").length == 0){
                this._super.apply(this, arguments);
            } else{
                ProductConfiguratorMixin._onChangeCombinationGroup(ev, $parent, combination);
            }
        }
    });
    return ProductConfiguratorMixin;

});