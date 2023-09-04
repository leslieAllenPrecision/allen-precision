from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
import xml.etree.ElementTree as ET
import base64
from datetime import timedelta,datetime
import logging
_logger = logging.getLogger(__name__)

class GoogleFeedConfig(models.Model):
    _name='google.feed.config'

    @api.model
    def default_get(self,fields):
        res = super(GoogleFeedConfig,self).default_get(fields)
        default_column_lst = ['id','name','description','barcode','categ_id','default_code']
        fields_of_product_template = self.env['ir.model.fields'].search([('name','in',default_column_lst),('model','=','product.template')]) 
        default_columns_for_field_mapping = {'product_g_id':'id','title':'name','description':'description','gtin':'default_code','brand':'categ_id','mpn':'barcode'}
        for map_key,map_value in default_columns_for_field_mapping.items():
            for field_id in fields_of_product_template:
                if field_id.name == map_value:
                    res[map_key] = field_id.id
                    break
        return res

    def default_product_price(self):
        res_model, res_id = self.env['ir.model.data'].check_object_reference('product', 'list0')
        res= self.env['product.pricelist'].browse(res_id)
        return res.id

    name = fields.Char('Feed Name')
    file_name = fields.Char('File Name')
    file_type = fields.Selection([('xml', 'XML'),('txt', 'TXT'),], string='File Type',default='xml')
    product_pricelist_id=fields.Many2one('product.pricelist',string='Pricelist',default=default_product_price)                             
    active = fields.Boolean(string = 'Active', default=True)
    auto_generate = fields.Boolean('Auto generate',help='You can auto generate the feed. You will get the option to set the interval for feed auto generation.')
    exclude_out_of_stock_products = fields.Boolean('Exclude Out Of stock Products')
    is_upload_to_server = fields.Boolean(string='Upload To Server')
    server_id = fields.Many2one('server.config',string='Server Name')
    server_path = fields.Char('Server Path')
    feed_file = fields.Binary('Generated File')
    attachment_id = fields.Many2one('ir.attachment',string='Attachment')
    interval_number = fields.Integer('Interval Number',default=1)
    interval_type = fields.Selection([('hours', 'Hours'),('days', 'Days'),('weeks', 'Weeks'),('months', 'Months')], string='Interval Unit', default='days')
    next_execution_time = fields.Datetime('Next Execution')  
    is_add_all_products = fields.Boolean('All Products',default=True) 
    product_ids =  fields.Many2many('product.template',string='Select Products')                              
    error_log_ids = fields.One2many('feed.process.error.log','feed_id',string='Error')
    description = fields.Many2one('ir.model.fields',string='Description')
    condition = fields.Selection([('new','New'),('refurbished','Refurbished'),('used','Used')],string='Condition',default='new')
    gtin = fields.Many2one('ir.model.fields',string='GTIN')
    brand = fields.Many2one('ir.model.fields',string='Brand')
    mpn = fields.Many2one('ir.model.fields',string='MPN')
    product_g_id = fields.Many2one('ir.model.fields',string='ID')
    title = fields.Many2one('ir.model.fields',string='Title')

    @api.onchange('file_name','file_type')
    def onchange_file_name(self):
        if self.file_name:
            split_name = self.file_name.split('.')
            if self.file_type == 'xml':
                self.file_name=("%s.xml" %(split_name[0]))
            elif self.file_type == 'txt':
                self.file_name=("%s.txt" %(split_name[0]))

    def add_to_google_feed(self):
        product_obj = self.env['product.template']
        error_log_obj = self.env['feed.process.error.log']
        root = ET.Element('channel')
        product_list = []
        if self.is_add_all_products:
            product_ids = product_obj.search([])
        else:
            product_ids = self.product_ids    
        try:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            for product in product_ids:
                product_avaibility = 'out of stock'   
                if self.exclude_out_of_stock_products and product.qty_available <= 0: 
                    continue
                if not self.check_relational_field_value(product,[self.product_g_id,self.title,self.description,self.gtin,self.brand]):
                    continue 
                if not self.check_madetory_field_value(product,[self.product_g_id.name,self.title.name,self.description.name,self.gtin.name,self.brand.name,self.mpn.name]):
                    continue
                if product.qty_available > 0:      
                    product_avaibility = 'in stock'
                price = self.product_pricelist_id and product.with_context(pricelist = self.product_pricelist_id.id).price or product.standard_price or 0.0
                currency = self.product_pricelist_id and self.product_pricelist_id.currency_id and self.product_pricelist_id.currency_id.name or product.currency_id.name    
                feed_data = {'g:id': str(self.get_value_from_field(product,self.product_g_id)),
                             'g:title':str(self.get_value_from_field(product,self.title)),
                             'g:description':str(self.get_value_from_field(product,self.description)),
                             'g:link': base_url +"/shop/product/%s" % slug(product),
                             'g:image_link':base_url + self.env['website'].image_url(product, 'image_1024'),
                             'g:condition':self.condition,
                             'g:price': str(str(price) +' %s' %(currency)),
                             'g:availability':str(product_avaibility),
                             'g:gtin':str(self.get_value_from_field(product,self.gtin)),
                             'g:brand':str(self.get_value_from_field(product,self.brand)),
                             'g:mpn':str(self.get_value_from_field(product,self.mpn)),}
                product_list.append(feed_data)           
            if not product_list:
                error_log_obj.create({'feed_id':self.id,'error_datetime':datetime.now(),'error_message':'According to the feed configuration, Not any product include in the feed','file_name':self.file_name})
            else:
                if self.file_type == "xml":
                    default_string ="<?xml version='1.0'?><rss version='2.0' xmlns:g='http://base.google.com/ns/1.0'>"
                    title = ET.SubElement(root, 'title')
                    title.text = 'Google Feed Data'
                    link=ET.SubElement(root, 'link')
                    link.text=base_url
                    description = ET.SubElement(root, 'description')
                    description.text = 'Google Product Feed Data'
                    for product_dict in product_list:
                        item = ET.SubElement(root,'item')
                        for data_key,data_value in product_dict.items():
                            item_tag = ET.SubElement(item,data_key)
                            item_tag.text = str(data_value)
                    if root:
                        final_string = default_string + (str(ET.tostring(root),'utf-8')) + "</rss>"
                        file_data = bytes(final_string,'utf-8')
                        self.feed_file=base64.encodestring(file_data)
                else:
                    header_string = ("id"+"\t"+"title"+"\t"+"description"+"\t"+"link"+"\t"+"image_link"+"\t"+"condition"+"\t"+"price"+"\t"+"availability"+"\t"+"gtin"+"\t"+"brand"+"\t"+"mpn"+"\n")            
                    final_string = ""
                    for i in product_list:
                        final_string += ('\t'.join(i.values())) + "\n"
                    file_data = bytes(header_string+final_string,'utf-8')
                    self.feed_file=base64.encodestring(file_data)   
                if self.feed_file and self.server_id:
                    self.server_id.upload_feed_on_server(self)
        except Exception as e:
            error_log_obj.create({'feed_id':self.id,'error_datetime':datetime.now(),'error_message':str(e),'file_name':self.file_name})
    
    @api.model                
    def auto_generate_google_feed(self):
        google_feed_ids = self.search([('auto_generate','=',True),'|',('next_execution_time','=',False),('next_execution_time','<=',datetime.now())])
        for record in google_feed_ids:
            record.add_to_google_feed()
            feed_next_execution_date = record.next_execution_time
            if not feed_next_execution_date:
                feed_next_execution_date = datetime.now() 
            next_execution_date = False
            if record.interval_type == 'hours':
                next_execution_date = feed_next_execution_date + timedelta(hours=record.interval_number)
            elif record.interval_type == 'days':
                next_execution_date = feed_next_execution_date + timedelta(days=record.interval_number)
            elif record.interval_type == "weeks":
                next_execution_date = feed_next_execution_date + timedelta(weeks=record.interval_number)
            elif record.interval_type == "months":
                next_execution_date = feed_next_execution_date + relativedelta(months=record.interval_number)
            if next_execution_date:
                record.write({'next_execution_time': next_execution_date})
            
    def check_madetory_field_value(self,product,field_list):
        error_log_obj = self.env['feed.process.error.log']
        error_message = ''
        for field in field_list:
            if not hasattr(product, field):    
                error_message = 'Please set mandatory field  %s' %(self.env['product.template']._fields[field].string)
                break 
            elif not getattr(product, field):
                model_id = self.env['ir.model'].search([('model','=','product.product')],limit=1) 
                if model_id:
                    field_type = self.env['ir.model.fields'].search([('name','=',field),('model_id','=',model_id.id)],limit=1)
                    if field_type and field_type.ttype == 'integer' or field_type.ttype == 'float':
                        pass
                    else:
                        error_message = 'Please set mandatory field : %s of %s ' %(field,product.name)
                        break


   
        if error_message:
            error_log_obj.create({'feed_id':self.id,'error_datetime':datetime.now(),'error_message':error_message,'product_id':product and product.id,'file_name':self.file_name})
            return False
        else:
            return True    
    
    def check_relational_field_value(self,product,list_field_name):
        value = False
        is_error = True
        error_log_obj = self.env['feed.process.error.log']
        error_message = ''
        for field_name in list_field_name:
            try:
                value = (eval('product.%s' %(field_name.name)))
            except Exception as e:
                error_log_obj.create({'feed_id':self.id,'error_datetime':datetime.now(),'error_message':str(e),'product_id':product and product.id,'file_name':self.file_name})
                is_error = False
                break;
            if value:
                if field_name.ttype=='many2one':
                    if not hasattr(value, 'name'):
                        error_message = 'You can not set the reference as relational model which do not have name column.'
                        error_log_obj.create({'feed_id':self.id,'error_datetime':datetime.now(),'error_message':error_message,'product_id':product and product.id,'file_name':self.file_name})
                        is_error = False
                        break;
                    elif not getattr(value, 'name'):
                        error_message = 'You  %s' %(field_name.relation)
                        error_log_obj.create({'feed_id':self.id,'error_datetime':datetime.now(),'error_message':error_message,'product_id':product and product.id,'file_name':self.file_name})
                        is_error = False
                        break;
                    else:
                        value = value.name
        return is_error
    
    def get_value_from_field(self,product,field_name):
        value = False
        error_log_obj = self.env['feed.process.error.log']
        error_message = ''
        try:
            value = (eval('product.%s' %(field_name.name)))
        except Exception as e:
            error_log_obj.create({'feed_id':self.id,'error_datetime':datetime.now(),'error_message':str(e),'product_id':product and product.id,'file_name':self.file_name})
            return False
        if value:
            if field_name.ttype=='many2one':
                if not hasattr(value, 'name'):
                    error_message = 'You can not set the reference as relational model which do not have name column.'
                    error_log_obj.create({'feed_id':self.id,'error_datetime':datetime.now(),'error_message':error_message,'product_id':product and product.id,'file_name':self.file_name})
                elif not getattr(value, 'name'):
                    error_message = 'You  %s' %(field_name.relation)
                    error_log_obj.create({'feed_id':self.id,'error_datetime':datetime.now(),'error_message':error_message,'product_id':product and product.id,'file_name':self.file_name})
                else:
                    return value.name
        return value

        