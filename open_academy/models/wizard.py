# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Wizard(models.TransientModel):
    _name = 'openacademy.wizard'
    _description = "Wizzard is for add attendees in session"

    def _default_sessions(self):
        return self.env['openacademy.sessions'].browse(self._context.get('active_ids'))

    session_ids = fields.Many2many('openacademy.sessions',
        string="Sessions", required=True, default=_default_sessions)

    register_partners = fields.Many2many('res.partner', string="Attendees")
    def subscribe(self):
        for session in self.session_ids:
            session.register_partners |= self.register_partners
        return {}
