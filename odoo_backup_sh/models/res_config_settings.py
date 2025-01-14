# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_odoo_backup_sh_google_disk = fields.Boolean(string="Google Drive", help="Use Google Drive to store Database")
    module_odoo_backup_sh_dropbox = fields.Boolean(string="Dropbox", help="Use Dropbox to store Database")
    available_module_odoo_backup_sh_dropbox = fields.Boolean()
    available_module_odoo_backup_sh_google_disk = fields.Boolean()
    odoo_backup_sh_amazon_bucket_name = fields.Char("S3 Bucket", config_parameter='odoo_backup_sh.s3_bucket_name', default='')
    odoo_backup_sh_amazon_access_key_id = fields.Char("Access Key ID", config_parameter='odoo_backup_sh.aws_access_key_id', default='')
    odoo_backup_sh_amazon_secret_access_key = fields.Char("Secret Access Key", config_parameter='odoo_backup_sh.aws_secret_access_key', default='')
    odoo_backup_sh_private_s3_dir = fields.Char("Path", config_parameter='odoo_backup_sh.private_s3_dir', default='', help="Folder in S3 Bucket, e.g. odoo-backups")
    odoo_backup_sh_odoo_oauth_uid = fields.Char("Odoo OAuth", config_parameter='odoo_backup_sh.odoo_oauth_uid', default='')
    private_s3_dir_changed = fields.Boolean(default=False)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrModule = self.env['ir.module.module']
        for m in ['odoo_backup_sh_google_disk', 'odoo_backup_sh_dropbox']:
            res['available_module_' + m] = bool(IrModule.sudo().search([('name', '=', m)], limit=1))
        get_param = self.env['ir.config_parameter'].get_param
        res.update(
            odoo_backup_sh_amazon_bucket_name=get_param('odoo_backup_sh.s3_bucket_name'),
            odoo_backup_sh_amazon_access_key_id=get_param('odoo_backup_sh.aws_access_key_id'),
            odoo_backup_sh_amazon_secret_access_key=get_param('odoo_backup_sh.aws_secret_access_key'),
            odoo_backup_sh_private_s3_dir=get_param('odoo_backup_sh.private_s3_dir'),
            odoo_backup_sh_odoo_oauth_uid=get_param('odoo_backup_sh.odoo_oauth_uid')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].set_param
        set_param('odoo_backup_sh.s3_bucket_name', self.odoo_backup_sh_amazon_bucket_name)
        set_param('odoo_backup_sh.aws_access_key_id', self.odoo_backup_sh_amazon_access_key_id)
        set_param('odoo_backup_sh.aws_secret_access_key', self.odoo_backup_sh_amazon_secret_access_key)
        set_param('odoo_backup_sh.odoo_oauth_uid', self.odoo_backup_sh_odoo_oauth_uid)
        set_param('odoo_backup_sh.private_s3_dir', self.odoo_backup_sh_private_s3_dir)

    @api.onchange('odoo_backup_sh_amazon_access_key_id')
    def switch_to_private_s3(self):
        if self.odoo_backup_sh_amazon_access_key_id and \
           self.odoo_backup_sh_amazon_access_key_id \
           != self.env['ir.config_parameter'].get_param('odoo_backup_sh.aws_access_key_id'):
            # when Access Key is changed to new non-empty value
            self.odoo_backup_sh_odoo_oauth_uid = ''

    @api.onchange('odoo_backup_sh_private_s3_dir')
    def track_dir_changes(self):
        current_value = self.env['ir.config_parameter'].get_param('odoo_backup_sh.private_s3_dir')
        has_key = self.env['ir.config_parameter'].get_param('odoo_backup_sh.aws_access_key_id')
        if self.odoo_backup_sh_private_s3_dir and \
           has_key and \
           self.odoo_backup_sh_private_s3_dir != current_value:
            self.private_s3_dir_changed = True
