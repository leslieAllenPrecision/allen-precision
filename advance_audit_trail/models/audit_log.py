# See LICENSE file for full copyright and licensing details.
"""Initialize All the python files."""

import httpagentparser

from odoo import fields, models
from odoo.http import request

from odoo.addons.auditlog.models.rule import DictDiffer

EMPTY_DICT = {}


class AuditlogLog(models.Model):
    """Inherited AuditLog model."""

    _inherit = "auditlog.log"

    ip_address = fields.Char(string="IP Address")
    platform_info = fields.Char(
        string="Platform Information",
        help="Platform Information which \
                                is used by user.",
    )
    os_type = fields.Char(string="Type of OS", help="Platform Operating system.")
    terminal = fields.Char(
        string="Browser Name & Version", help="Browser Name & Version"
    )


class AuditlogRule(models.Model):
    """Inherited AuditLog model."""

    _inherit = "auditlog.rule"

    def create_logs(
        self,
        uid,
        res_model,
        res_ids,
        method,
        old_values=None,
        new_values=None,
        additional_log_values=None,
    ):
        """Overwritten create_logs method.

        Create logs. `old_values` and `new_values` are dictionaries, e.g:
        {RES_ID: {'FIELD': VALUE, ...}}
        Overwritten create_logs method to update the IP, OS and Terminal
        related information.
        """
        if old_values is None:
            old_values = EMPTY_DICT
        if new_values is None:
            new_values = EMPTY_DICT
        log_model = self.env["auditlog.log"]
        http_request_model = self.env["auditlog.http.request"]
        http_session_model = self.env["auditlog.http.session"]
        model_id = self.pool._auditlog_model_cache[res_model]
        auditlog_rule = self.env["auditlog.rule"].search([("model_id", "=", model_id)])
        fields_to_exclude = auditlog_rule.fields_to_exclude_ids.mapped("name")
        for res_id in res_ids:
            model_model = self.env[res_model]
            name = model_model.browse(res_id).name_get()
            res_name = name and name[0] and name[0][1]
            ip_add = str(
                "X-Real-IP" in request.httprequest.headers
                and request.httprequest.headers.get("X-Real-IP")
                or request.httprequest.remote_addr
                or ""
            )
            user_agent = httpagentparser.detect(
                request.httprequest.headers.get("User-Agent")
            )
            terminal = "{} {}".format(
                str(user_agent.get("browser", {}).get("name", "")),
                str(user_agent.get("browser", {}).get("version", "")),
            )
            platform_version = str(user_agent.get("platform", {}).get("version", ""))
            if platform_version == "None":
                platform_version = ""
            platform_info = "{} {}".format(
                str(user_agent.get("platform", {}).get("name", "")), platform_version,
            )
            vals = {
                "name": res_name,
                "model_id": self.pool._auditlog_model_cache[res_model],
                "res_id": res_id,
                "method": method,
                "user_id": uid,
                "http_request_id": http_request_model.current_http_request(),
                "http_session_id": http_session_model.current_http_session(),
                "ip_address": ip_add,
                "os_type": str(user_agent.get("os", {}).get("name", "")),
                "terminal": terminal,
                "platform_info": platform_info,
            }
            vals.update(additional_log_values or {})
            log = log_model.create(vals)
            diff = DictDiffer(
                new_values.get(res_id, EMPTY_DICT), old_values.get(res_id, EMPTY_DICT)
            )
            if method == "create":
                self._create_log_line_on_create(log, diff.added(), new_values, fields_to_exclude)
            elif method == "read":
                self._create_log_line_on_read(
                    log, old_values.get(res_id, EMPTY_DICT).keys(), old_values, fields_to_exclude
                )
            elif method == "write":
                self._create_log_line_on_write(
                    log, diff.changed(), old_values, new_values, fields_to_exclude
                )
