# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
"""
Describes configuration for Magento Instance.
"""
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.http import request

MAGENTO_FINANCIAL_STATUS_EPT = 'magento.financial.status.ept'
STOCK_WAREHOUSE = 'stock.warehouse'


class ResConfigSettings(models.TransientModel):
    """
    Describes Magento Instance Configurations
    """
    _inherit = 'res.config.settings'

    def _get_magento_default_financial_statuses(self):
        if self._context.get('default_magento_instance_id', False):
            financial_status_ids = self.env[MAGENTO_FINANCIAL_STATUS_EPT].search(
                [('magento_instance_id', '=',
                  self._context.get('default_magento_instance_id', False))]).ids
            return [(6, 0, financial_status_ids)]
        return [(6, 0, [])]

    magento_instance_id = fields.Many2one(
        'magento.instance',
        'Instance',
        ondelete='cascade',
        help="This field relocates magento instance"
    )

    magento_website_id = fields.Many2one(
        'magento.website',
        string="Website",
        help="Magento Websites",
        domain="[('magento_instance_id', '=', magento_instance_id)]"
    )

    magento_storeview_id = fields.Many2one(
        'magento.storeview',
        string="Storeviews",
        help="Magento Storeviews",
        domain="[('magento_website_id', '=', magento_website_id)]"
    )

    magento_team_id = fields.Many2one('crm.team', string='Sales Team', help="Sales Team")

    magento_sale_prefix = fields.Char(
        string="Sale Order Prefix",
        help="A prefix put before the name of imported sales orders.\n"
             "For example, if the prefix is 'mag-', the sales "
             "order 100000692 in Magento, will be named 'mag-100000692' in ERP."
    )
    magento_website_warehouse_id = fields.Many2one(
        STOCK_WAREHOUSE,
        string='Warehouse',
        help='Warehouse to be used to deliver an order from this website.'
    )
    warehouse_ids = fields.Many2many(
        STOCK_WAREHOUSE,
        string="Warehouses",
        help='Warehouses used to compute stock to update on Magento.'
    )
    catalog_price_scope = fields.Selection([
        ('global', 'Global'),
        ('website', 'Website')
    ], string="Magento Catalog Price Scope", help="Scope of Price in Magento", default='global')
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string="Pricelist",
        help="Product price will be taken/set from this pricelist if Catalog Price Scope is global"
    )

    allow_import_image_of_products = fields.Boolean(
        "Import Images of Products",
        default=False,
        help="Import product images along with product from Magento while import product?"
    )
    # Import Product Stock
    is_import_product_stock = fields.Boolean(
        'Is Import Magento Product Stock?',
        default=False,
        help="Import Product Stock from Magento to Odoo"
    )
    import_stock_warehouse = fields.Many2one(
        STOCK_WAREHOUSE,
        string="Import Product Stock Warehouse",
        help="Warehouse for import stock from Magento to Odoo"
    )
    magento_stock_field = fields.Selection([
        ('free_qty', 'Free Quantity'),
        ('virtual_available', 'Forecast Quantity')
    ], string="Magento Stock Type", default='free_qty', help="Magento Stock Type")
    auto_create_product = fields.Boolean(
        string="Automatically Create Odoo Product If Not Found?",
        default=False,
        help="If checked, It will create new odoo products, if not found while import products/ orders. "
             "\nIf not checked, Queue will be failed while import order or product and product not found."
    )
    is_use_odoo_order_sequence = fields.Boolean(
        "Is Use Odoo Order Sequences?",
        default=False,
        help="If checked, Odoo Order Sequence is used when import and create orders."
    )
    invoice_done_notify_customer = fields.Boolean(
        string="Invoices Done Notify customer",
        default=False,
        help="while export invoice send email to the customer"
    )
    import_magento_order_status_ids = fields.Many2many(
        'import.magento.order.status',
        'magento_config_settings_order_status_rel',
        'magento_config_id', 'status_id',
        "Import Order Status",
        help="Select order status in which you want to import the orders from Magento to Odoo.")
    is_multi_warehouse_in_magento = fields.Boolean(
        string="Is Multi Warehouse in Magento?",
        default=False,
        help="If checked, Multi Warehouse used in Magento"
    )
    magento_website_pricelist_ids = fields.Many2many(
        'product.pricelist',
        string="Magento Pricelist",
        help="Product price will be taken/set from this pricelist if Catalog Price Scope is website"
    )

    magento_version = fields.Selection([
        ('2.1', '2.1+'),
        ('2.2', '2.2+'),
        ('2.3', '2.3+')
    ], string="Magento Versions", required=True, help="Version of Magento Instance", default='2.2')
    magento_url = fields.Char(string='Magento URLs', required=False, help="URL of Magento")
    import_product_category = fields.Many2one(
        'product.category',
        string="Import Product Category",
        help="While importing a product, "
             "the selected category will set in that product."
    )
    magento_financial_status_ids = fields.Many2many(
        MAGENTO_FINANCIAL_STATUS_EPT,
        'magento_sale_auto_workflow_conf_rel',
        'financial_onboarding_status_id', 'workflow_id',
        string='Magento Financial Status', default=_get_magento_default_financial_statuses)

    dashboard_view_type = fields.Selection(
        [('instance_level', 'Instance Level'), ('website_level', 'Website Level')],
        'View Dashboard Based on',
        config_parameter='odoo_magento2_ept.dashboard_view_type',
        default='website_level')
    import_order_after_date = fields.Datetime(
        help="Connector only imports those orders which have created after a given date.")
    tax_calculation_method = fields.Selection([
        ('excluding_tax', 'Excluding Tax'), ('including_tax', 'Including Tax')],
        string="Tax Calculation Method into Magento Website", default="excluding_tax",
        help="This indicates whether product prices received from Magento is including tax or excluding tax,"
             " when import sale order from Magento"
    )
    magento_set_sales_description_in_product = fields.Boolean(
        string="Use Sales Description of Magento Product",
        config_parameter="odoo_magento2_ept.set_magento_sales_description",
        help="In both odoo products and Magento layer products, it is used to set the description and short description"
    )
    module_odoo_magento2_extended_bundle_products_order_ept = fields.Boolean(
        'Import bundle product orders from Magento?',
        help="If Yes, then mrp module will be install in the database.")
    magento_apply_tax_in_order = fields.Selection(
        [("odoo_tax", "Odoo Default Tax Behaviour"), ("create_magento_tax",
                                                      "Create New Tax If Not Found")],
        copy=False, default="create_magento_tax", help=""" For Magento Orders :- \n
                        1) Odoo Default Tax Behaviour - The Taxes will be set based on Odoo's default functional 
                        behaviour i.e. based on Odoo's Tax and Fiscal Position configurations. \n
                        2) Create New Tax If Not Found - System will search the tax data received 
                        from Magento in Odoo, will create a new one if it fails in finding it.""")

    magento_invoice_tax_account_id = fields.Many2one("account.account", string="Invoice Tax Account For Magento Tax")
    magento_credit_tax_account_id = fields.Many2one("account.account", string="Credit Note Tax Account For Magento Tax")
    magento_tax_rounding_method = fields.Selection(
        [("round_per_line", "Round per Line"), ("round_globally", "Round Globally")], default="round_per_line")
    magento_analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    magento_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tag')

    @api.onchange('magento_instance_id')
    def onchange_magento_instance_id(self):
        """
        Sets default values for configuration when change/ select Magento Instance.
        """
        magento_instance_id = self.magento_instance_id
        if magento_instance_id:
            self.write({
                'warehouse_ids': [
                    (6, 0,
                     magento_instance_id.warehouse_ids.ids)] if magento_instance_id.warehouse_ids else False,
                'magento_stock_field': magento_instance_id.magento_stock_field,
                'magento_version': magento_instance_id.magento_version,
                'auto_create_product': magento_instance_id.auto_create_product,
                'allow_import_image_of_products': magento_instance_id.allow_import_image_of_products,
                'catalog_price_scope': magento_instance_id.catalog_price_scope,
                'is_multi_warehouse_in_magento': magento_instance_id.is_multi_warehouse_in_magento,
                'pricelist_id': magento_instance_id.pricelist_id.id if magento_instance_id.pricelist_id else False,
                'is_import_product_stock': magento_instance_id.is_import_product_stock,
                'import_stock_warehouse': magento_instance_id.import_stock_warehouse.id if magento_instance_id.import_stock_warehouse else False,
                'invoice_done_notify_customer': magento_instance_id.invoice_done_notify_customer,
                'import_magento_order_status_ids': magento_instance_id.import_magento_order_status_ids.ids,
                'import_product_category': magento_instance_id.import_product_category if magento_instance_id.import_product_category else False,
                'import_order_after_date': magento_instance_id.import_order_after_date or False,
                'magento_apply_tax_in_order': magento_instance_id.magento_apply_tax_in_order,
                'magento_invoice_tax_account_id': magento_instance_id.magento_invoice_tax_account_id,
                'magento_credit_tax_account_id': magento_instance_id.magento_credit_tax_account_id,
                'magento_tax_rounding_method': magento_instance_id.magento_tax_rounding_method,
                'magento_analytic_account_id': magento_instance_id.magento_analytic_account_id,
                'magento_analytic_tag_ids': magento_instance_id.magento_analytic_tag_ids,
                # 'is_export_dropship_picking': magento_instance_id.is_export_dropship_picking if magento_instance_id.is_export_dropship_picking else False
            })
        else:
            self.magento_instance_id = False

    @api.onchange('magento_website_pricelist_ids')
    def onchange_magento_website_pricelist_ids(self):
        if self.magento_website_id:
            self.magento_website_id.write(
                {'pricelist_ids': [(6, 0, self.magento_website_pricelist_ids.ids)]})

    @api.onchange('magento_website_id')
    def onchange_magento_website_id(self):
        """
        set some Magento configurations based on changed Magento instance.
        """
        magento_website_id = self.magento_website_id
        self.magento_storeview_id = self.magento_website_warehouse_id = self.magento_website_pricelist_ids = False
        if magento_website_id:
            if magento_website_id.pricelist_ids.ids:
                self.magento_website_pricelist_ids = magento_website_id.pricelist_ids.ids
            if magento_website_id.warehouse_id:
                self.magento_website_warehouse_id = magento_website_id.warehouse_id.id
            self.tax_calculation_method = magento_website_id.tax_calculation_method

    @api.onchange('magento_storeview_id')
    def onchange_magento_storeview_id(self):
        """
        set some Magento configurations based on changed Magento instance.
        """
        magento_storeview_id = self.magento_storeview_id
        self.is_use_odoo_order_sequence = self.magento_team_id = False
        self.magento_sale_prefix = ''
        if magento_storeview_id:
            if magento_storeview_id.team_id:
                self.magento_team_id = magento_storeview_id.team_id.id
            self.magento_sale_prefix = magento_storeview_id.sale_prefix
            self.is_use_odoo_order_sequence = magento_storeview_id.is_use_odoo_order_sequence

    def execute(self):
        """
        Save all selected Magento Instance configurations
        """
        magento_instance_id = self.magento_instance_id
        res = super(ResConfigSettings, self).execute()
        if magento_instance_id:
            self.write_instance_vals(magento_instance_id)
        if self.magento_website_id:
            self.magento_website_id.write({
                'warehouse_id': self.magento_website_warehouse_id.id,
                'tax_calculation_method': self.tax_calculation_method,
            })
        if self.magento_storeview_id:
            self.magento_storeview_id.write({
                'team_id': self.magento_team_id,
                'sale_prefix': self.magento_sale_prefix,
                'is_use_odoo_order_sequence': self.is_use_odoo_order_sequence
            })
        return res

    def write_instance_vals(self, magento_instance_id):
        """
        Write values in the instance
        :param magento_instance_id: instance ID
        :return:
        """
        values = {}
        values.update({
            'warehouse_ids': [(6, 0, self.warehouse_ids.ids)] if self.warehouse_ids else False,
            'magento_stock_field': self.magento_stock_field,
            'auto_create_product': self.auto_create_product,
            'catalog_price_scope': magento_instance_id.catalog_price_scope if magento_instance_id else False,
            'allow_import_image_of_products': self.allow_import_image_of_products,
            'pricelist_id': self.pricelist_id.id if self.pricelist_id else False,
            'is_import_product_stock': self.is_import_product_stock,
            'import_stock_warehouse': self.import_stock_warehouse.id if self.import_stock_warehouse else False,
            'invoice_done_notify_customer': self.invoice_done_notify_customer,
            'import_magento_order_status_ids': [(6, 0, self.import_magento_order_status_ids.ids)],
            'is_multi_warehouse_in_magento': self.is_multi_warehouse_in_magento if self.is_multi_warehouse_in_magento else False,
            'import_product_category': self.import_product_category if self.import_product_category else "",
            'import_order_after_date': self.import_order_after_date if self.import_order_after_date else "",
            'magento_apply_tax_in_order': self.magento_apply_tax_in_order,
            'magento_invoice_tax_account_id': self.magento_invoice_tax_account_id,
            'magento_credit_tax_account_id': self.magento_credit_tax_account_id,
            'magento_tax_rounding_method': self.magento_tax_rounding_method,
            'magento_analytic_account_id': self.magento_analytic_account_id,
            'magento_analytic_tag_ids': self.magento_analytic_tag_ids,
            # 'is_export_dropship_picking': self.is_export_dropship_picking if self.is_export_dropship_picking else ""
        })
        magento_instance_id.write(values)

    @api.model
    def action_magento_open_basic_configuration_wizard(self):
        """
        Called by on boarding panel above the Instance.
        return the action for open the basic configurations wizard
        :return: True
        """
        try:
            view_id = self.env.ref(
                'odoo_magento2_ept.magento_basic_configurations_onboarding_wizard_view')
        except Exception:
            return True
        return self.magento_res_config_view_action(view_id)

    @api.model
    def action_magento_open_financial_status_wizard(self):
        """
        Called by onboarding panel above the Instance.
        Return the action for open the basic configurations wizard
        :return: True
        """
        try:
            view_id = self.env.ref(
                'odoo_magento2_ept.magento_financial_status_onboarding_wizard_view')
        except Exception:
            return True
        return self.magento_res_config_view_action(view_id)

    def magento_res_config_view_action(self, view_id):
        """
        Return the action for open the configurations wizard
        :param view_id: XML View Id
        :return:
        """
        magento_instance_obj = self.env['magento.instance']
        action = self.env["ir.actions.actions"]._for_xml_id(
            "odoo_magento2_ept.action_magento_config_settings")
        action_data = {'view_id': view_id.id, 'views': [(view_id.id, 'form')], 'target': 'new',
                       'name': 'Configurations'}
        instance = magento_instance_obj.search_magento_instance()
        if instance:
            action['context'] = {'default_magento_instance_id': instance.id}
        else:
            action['context'] = {}
        action.update(action_data)
        return action

    def magento_save_basic_configurations(self):
        """
        Save the basic configuration changes in the instance
        :return: True
        """
        magento_instance_id = self.magento_instance_id
        if magento_instance_id:
            basic_onboard_configurations = {
                'warehouse_ids': [
                    (6, 0, self.warehouse_ids.ids)] if self.warehouse_ids else False,
                'magento_stock_field': self.magento_stock_field,
                'auto_create_product': self.auto_create_product,
                'allow_import_image_of_products': self.allow_import_image_of_products,
                'catalog_price_scope': self.catalog_price_scope,
                'is_multi_warehouse_in_magento': self.is_multi_warehouse_in_magento,
                'pricelist_id': self.pricelist_id.id if self.pricelist_id else False,
                'is_import_product_stock': self.is_import_product_stock,
                'import_stock_warehouse': self.import_stock_warehouse.id if self.import_stock_warehouse else False,
                'invoice_done_notify_customer': self.invoice_done_notify_customer,
                'import_magento_order_status_ids': self.import_magento_order_status_ids.ids,
                'import_product_category': self.import_product_category if self.import_product_category else "",
                'import_order_after_date': self.import_order_after_date if self.import_order_after_date else "",
                'magento_apply_tax_in_order': self.magento_apply_tax_in_order,
                'magento_invoice_tax_account_id': self.magento_invoice_tax_account_id,
                'magento_credit_tax_account_id': self.magento_credit_tax_account_id,
                'magento_tax_rounding_method': self.magento_tax_rounding_method,
                'magento_analytic_account_id': self.magento_analytic_account_id,
                'magento_analytic_tag_ids': self.magento_analytic_tag_ids,
                # 'is_export_dropship_picking': magento_instance_id.is_export_dropship_picking if magento_instance_id.is_export_dropship_picking else False
            }
            magento_instance_id.write(basic_onboard_configurations)
            company = magento_instance_id.company_id
            company.set_onboarding_step_done('magento_basic_configuration_onboarding_state')
        if self.magento_website_id:
            self.magento_website_id.write({
                'warehouse_id': self.magento_website_warehouse_id.id,
                'tax_calculation_method': self.tax_calculation_method
            })
        if self.magento_storeview_id:
            self.magento_storeview_id.write({
                'team_id': self.magento_team_id,
                'sale_prefix': self.magento_sale_prefix,
                'is_use_odoo_order_sequence': self.is_use_odoo_order_sequence
            })
        return True

    def magento_save_financial_status_configurations(self):
        """
        Save the changes in the Instance.
        :return: True
        """
        magento_financial_status_obj = self.env[MAGENTO_FINANCIAL_STATUS_EPT]
        instance = self.magento_instance_id
        if instance:
            company = instance.company_id
            company.set_onboarding_step_done('magento_financial_status_onboarding_state')
            financials_status = magento_financial_status_obj.search(
                [('magento_instance_id', '=', instance.id)])
            unlink_for_financials_status = financials_status - self.magento_financial_status_ids
            unlink_for_financials_status.unlink()
        return True

    def download_bundle_product_module(self):
        """
        This method are used to find the bundle product module zip from attachment and
        download it.
        :return: odoo_magento2_bundle_product_order_ept.zip file.
        """
        attachment = self.env['ir.attachment'].sudo().search([
            ('name', '=', 'odoo_magento2_extended_bundle_products_order_ept.zip')], limit=1)
        if attachment:
            url = '/web/content/{}?download=true'.format(attachment.id)
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
                'nodestroy': False,
            }
        return UserError("Bundle product extended module is not found. "
                         "Please upgrade Magento Connector then try to download.")
