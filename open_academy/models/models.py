# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, exceptions, _
import logging
logger = logging.getLogger()

class course(models.Model):
    _name = 'openacademy.course'
    _rec_name = "title"
    _description = 'Course of academy'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'mail.thread','ir.attachment']
    _sql_constraints = [
        ('DESCRIPTION_CHECK',
         'CHECK(title != description)',
         "The title of the course can't be the description"),
        ('NAME_UNIQUE',
         'UNIQUE(title)',
         "The course title must be unique"),
    ]

    title = fields.Char(compute='_compute_instructor_name', store=True)
    description = fields.Text()
    responsible = fields.Many2one('res.users')
    datasesion = fields.One2many('openacademy.sessions','data_sessions',string='Session')
    name_course= fields.Char(store=True)
    picture = fields.Binary(string="Image")
    html_description = fields.Html(string='Description')
    files = fields.Many2many('ir.attachment', string='Archivos')
    gallery = fields.Many2many('openacademy.gallery',string="Carousel")
    
    @api.depends('datasesion.instructores')
    def _compute_instructor_name(self):
        for course in self:
            course.title = f"{course.name_course} - {course.responsible.name}"

    def copy(self, default=None):
        default = dict(default or {})
        copied_count = self.search_count([('title', '=like', _(u"Copy of {}%").format(self.title))])
        if not copied_count:
            new_name = _(u"Copy ({})").format(self.title)
        default['title'] = new_name
        return super(course, self).copy(default)
    
    

class sessions(models.Model):
    _name = 'openacademy.sessions'
    _rec_name='name'
    _description='Sessions of the course'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin']
    name = fields.Char()
    start_date = fields.Date(default=fields.Date.today)
    active = fields.Boolean(default=True)
    duration = fields.Float()
    duration_days = fields.Integer()
    seats = fields.Integer()
    maxseats = fields.Integer(default=1)
    color = fields.Integer()
    end_date = fields.Date(string="End Date", store=True,compute='_get_end_date', inverse='_set_end_date')
    instructores = fields.Many2one('res.partner',domain=['|', ('instructor', '=', True),('category_id.name', 'ilike', "Teacher")])
    register_partners = fields.Many2many('res.partner',string="Partners")
    data_sessions = fields.Many2one('openacademy.course',string="Course")
    taken_seats = fields.Integer(compute='_compute_taken_seats')
    attendees_total = fields.Integer(string="Total attendees", compute='_compute_attendees_total', store=True)
    # Mirar el porcentaje de asientos
    @api.depends('seats','maxseats')
    def _compute_taken_seats(self):
        for r in self:
            if r.seats > 0:
                r.taken_seats = (r.maxseats/r.seats) * 100
            else:
                r.taken_seats = 0
    # Warnings para los instructores
    @api.onchange('seats','instructores')
    def _verify_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': _("Incorrect 'seats' value"),
                    'message': _("The number of available seats may not be negative"),
                },
            }
        if self.seats < len(self.instructores):
            return {
                'warning': {
                    'title': _("Too many attendees"),
                    'message': _("Increase seats or remove excess attendees"),
                },
            }
    @api.depends('start_date', 'duration_days')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration_days):
                r.end_date = r.start_date
                continue

            start = fields.Datetime.from_string(r.start_date)
            duration = timedelta(days=r.duration_days, seconds=-1)
            r.end_date = start + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration_days = (end_date - start_date).days + 1

    @api.constrains('instructores', 'register_partners')
    def _check_instructor(self):
        for r in self:
            if r.instructores and r.instructores in r.register_partners:
                raise exceptions.ValidationError(_("A session's instructor can't be an attendee"))
    # Suma total de atendidos
    @api.depends('register_partners')
    def _compute_attendees_total(self):
        for r in self:
            r.attendees_total = len(r.register_partners)

class gallery(models.Model):
    _name = 'openacademy.gallery' 
    _description = 'Image Gallery'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    image = fields.Binary(string='Carousel')