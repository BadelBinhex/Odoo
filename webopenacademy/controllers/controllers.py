# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo import _
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging  
_logger = logging.getLogger(__name__)

class Webopenacademy(http.Controller):
    
    def _prepare_home_portal_values(self,counters):
        values = super()._prepare_home_portal_values(counters)
        count_sessions = http.request.env['openacademy.sessions'].search_count([('active','=',True)])
        values.update({
            'count_sessions': count_sessions,
        })
        return values
    #Mostrar todos los cursos
    @http.route(['/webopenacademy/list_courses/page/<page>','/webopenacademy/list_courses/','/'], type='http', website=True, auth="public")
    def list_courses(self,offset=None,search='',order='',filtre='',page=0, **post):
        actual_user = request.env.user.partner_id.id
        courses = request.env['openacademy.course'].sudo().search([])
        total_items= request.env['openacademy.course'].sudo().search_count([])
        
        if order:
            order_field =order.split(" ")
            if order_field[1]=="asc":
                courses = courses.sorted(str(order_field[0]))
            elif order_field[1]=="des":
                courses = courses.sorted(str(order_field[0]), reverse=True)
        if search:
            subdomains =[('title', 'ilike', search)]
            courses = courses.search(subdomains)    
        
        post['order'] = order
        post['filtre'] = filtre
        
        pager = request.website.pager(
            url='/webopenacademy/list_courses/',
            total=total_items,
            page=page,
            step=3,
            url_args=post,
        )
        joined_sessions = request.env['openacademy.sessions'].search([('register_partners', 'in', actual_user)])

        if filtre:
            courses = courses.filtered(lambda c: not c.sessions or all(session not in joined_sessions for session in c.sessions))
        keep = QueryURL('/webopenacademy/list_courses/', search=search, order=post.get('order'))

        offset = pager['offset']
        courses = courses[offset: offset +3]
        
        return request.render(
            'webopenacademy.list_courses',
            {'courses': courses, 'pager': pager,'search':search,'filtre': filtre,'order':order,'keep': keep,}
        )
        
    #Datos del curso actual
    @http.route('/webopenacademy/course/<int:course_id>/data',type='http',website=True,auth="public")
    def data_course(self,course_id,**kw):
        course_data=request.env['openacademy.course'].sudo().browse(course_id).id
        coursee=request.env['openacademy.course'].sudo().search([('id','=',int(course_data))])
        return request.render('webopenacademy.data_course',{'coursee':coursee,'imagenes':coursee.gallery,})
    #Archivos
    @http.route('/webopenacademy/course/<int:course_id>/archivos', type='http', website=True, auth="public")
    def archivos_curso(self, course_id, **kw):
        course = request.env['openacademy.course'].sudo().browse(course_id)
        id_curso =request.env['openacademy.course'].sudo().search([('id','=',course_id)])
        archivos = course.files
        _logger.info(f"\n\nArchivos del curso: {archivos}")
        return request.render('webopenacademy.archivos_curso', {'archivos': archivos,'id_curso':id_curso})

    #Página de sesiones
    @http.route('/webopenacademy/course/<int:session_id>/sessions', type='http', website=True, auth="public")
    def list_sessions(self,session_id, **kw):
        sessions = request.env['openacademy.sessions'].sudo().search(['|', ('id', '=', int(session_id)), ('active', '=', 'True'),('data_sessions','=',int(session_id))])
        course = request.env['openacademy.sessions'].sudo().search(['|', ('id', '=', int(session_id)), ('active', '=', 'True'),('data_sessions','=',int(session_id))]).data_sessions.title
        return request.render(
            'webopenacademy.list_sessions',
            {'sessions': sessions, 'course': course}
        )
    
    #Mostrar sesiones del usuario
    @http.route('/my/sessions', type='http', website=True, auth="public")
    def portal_my_sessions(self,**kw):
        partner = request.env.user.partner_id.id
        count_sessions = request.env['openacademy.sessions'].sudo().search_count([('active', '=', 'True')])
        sessions = request.env['openacademy.sessions'].sudo().search([('active', '=', 'True'),('register_partners','in', [partner])])
        return request.render(
            'webopenacademy.portal_my_sessions',
            {'count_sessions': count_sessions,'sessions':sessions}
        )
    #Mostrar datos de la sesión seleccionada
    @http.route('/my/sessions/<int:sessions_id>', type='http', website=True, auth="public")
    def data_sessions(self,sessions_id,**kw):
        partner = request.env.user.partner_id.id
        session_name= request.env['openacademy.sessions'].sudo().search([('id','=',int(sessions_id))]).name
        sessions = request.env['openacademy.sessions'].sudo().search(['|', ('id', '=', int(sessions_id)), ('active', '=', 'True'),('name','=',session_name)])
        return request.render('webopenacademy.data_sessions',{'sessions': sessions,'partner':partner})
    
    #Agregar usuario a la sesión
    @http.route('/my/sessions/<int:session_actual>/updated', type='http', website=True, auth="public")
    def new_partner(self,session_actual,**kw):
        partner_actual = request.env.user.partner_id.id
        sesion = request.env['openacademy.sessions'].sudo().search([('id','=',session_actual)])
        if partner_actual not in sesion.register_partners.mapped('id'):
            sesion.write({'register_partners': [(4, partner_actual)]})
            message = 'The actual user have resgistered without any problem'
            return request.render('webopenacademy.new_partner',{'message': message,'sesion':sesion})
    #Desvincular usuario de la sesión
    @http.route('/my/sessions/<int:session_actual>/unjoin', type='http', website=True, auth="public")
    def unjoin_partner(self,session_actual,**kw):
        user_id_actual = request.env.user.partner_id.id
        session = request.env['openacademy.sessions'].sudo().search([('id', '=', session_actual)])
        if session:
            new_values = [(3, user_id_actual)]
            session.write({'register_partners': new_values})

        message = "You have been unjoined of the session!"
        return request.render('webopenacademy.unjoin_partner', {'message': message})

    