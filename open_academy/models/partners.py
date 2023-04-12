# -*- coding: utf-8 -*-

from odoo import models, fields, api
class partners(models.Model):
    _inherit = 'res.partner'
    instructor = fields.Boolean()
    session_related_partner = fields.Many2many('openacademy.sessions')