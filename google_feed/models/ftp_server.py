from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ftplib import FTP
import base64
import io
from datetime import datetime
try:
    import paramiko
except ImportError:
    raise ImportError('This module needs paramiko to automatically write backups to the FTP through SFTP. '
        'Please install paramiko on your system. (sudo pip3 install paramiko)')

class ServerConfig(models.Model):
    _name='server.config'

    name = fields.Char('Server Name')
    host = fields.Char('Host')
    protocol = fields.Selection([('ftp','FTP'),('sftp','SFTP')],default="ftp", string='Protocol')
    user_name = fields.Char('User')
    password = fields.Char('Password')
    port = fields.Integer('Port')
    
    def authorize_FTP(self):
        client = None
        try:
            client = FTP()
            client.connect(self.host,self.port)
            client.login(self.user_name,self.password)
        except Exception as e:
            raise UserError(_('The server error is : %s ' %(str(e))))
        return client
    
    def authorize_SFTP(self):
        sftp_client = None
        try:
            sftp_client = paramiko.SSHClient()
            sftp_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sftp_client.connect(self.host, self.port, self.user_name, self.password, timeout=10)
        except Exception as e:
            raise UserError(_('The server error is : %s ' %(str(e))))
        return sftp_client        
    
    def test_server_connection(self):
        self.ensure_one()
        has_failed = False    
        if self.protocol=='ftp':
            client = None
            try:
                client = self.authorize_FTP()
            except Exception as e:
                has_failed = True
                raise UserError(_('The server error is : %s ' %(str(e))))
            finally:
                if client:
                    client.close()
        else:        
            sftp_client = None    
            try:
                sftp_client = self.authorize_SFTP()
            except Exception as e:
                has_failed = True
                raise UserError(_('The server error is : %s ' %(str(e))))
            finally:
                if sftp_client:
                    sftp_client.close()

        if not has_failed:
            title = _("Connection Test Succeeded!")
            message = _("Everything seems properly set up!")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': message,
                    'sticky': False,
                }
            }
            
    def upload_feed_on_server(self,feed_id):
        error_msg = ''
        if self.protocol == 'ftp':
            client = None
            try:
                client = self.authorize_FTP()
                if client:
                    client.cwd(feed_id.server_path)
                    data = base64.b64decode(feed_id.feed_file)
                    with io.BytesIO(data) as file:
                        client.storbinary('STOR %s' % feed_id.file_name, file)
            except Exception as e:
                error_msg = str(e)
            finally:
                if client:
                    client.close()
        else:
            sftp = None
            try:
                sftp = self.authorize_SFTP()
                if sftp:
                    data = base64.b64decode(feed_id.feed_file)
                    sftp_obj = sftp.open_sftp()
                    sftp_obj.chdir(feed_id.server_path)
                    with io.BytesIO(data) as file:
                        sftp_obj.putfo(file, feed_id.file_name)
                        sftp_obj.close()
            except Exception as e:
                error_msg = str(e)
            finally:
                if sftp:
                    sftp.close()
        if error_msg: 
            self.env['feed.process.error.log'].create({'feed_id':feed_id.id,'error_datetime':datetime.now(),'error_message':error_msg,'file_name':feed_id.file_name})