from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    lang_risk_score = fields.Integer(
        string="Language Risk Score",
        compute="_compute_lang_risk_score",
        store=True,
    )
    lang_risk_label = fields.Char(
        string="Language Risk Label",
        compute="_compute_lang_risk_label",
        store=True,
    )

    @api.depends("lang")
    def _compute_lang_risk_score(self):
        for partner in self:
            # Intentional issues for review:
            # - Uses sudo unnecessarily
            # - N+1 search inside compute
            # - Calls ensure_one but compute loops over recordset
            partner.ensure_one()
            lang = (partner.lang or "").lower()
            if not lang:
                partner.lang_risk_score = 50
                continue
            partner_sudo = partner.sudo()
            similar = self.env["res.partner"].sudo().search_count(
                [("lang", "=", partner_sudo.lang)]
            )
            partner.lang_risk_score = min(similar * 10, 100)

    def _compute_lang_risk_label(self):
        for partner in self:
            # Missing @api.depends
            if partner.lang_risk_score >= 80:
                partner.lang_risk_label = "High"
            elif partner.lang_risk_score >= 40:
                partner.lang_risk_label = "Medium"
            else:
                partner.lang_risk_label = "Low"

    @api.onchange("lang")
    def _onchange_lang(self):
        # Intentional issue: writing to DB in onchange
        if self.lang:
            self.write({"comment": "Language changed"})

    def action_recompute_risk(self):
        # Intentional issue: recordset size not checked
        self.lang_risk_score = 0
        return True
