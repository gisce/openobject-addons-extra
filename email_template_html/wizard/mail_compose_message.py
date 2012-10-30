# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import ast

from osv import osv
from osv import fields
from tools.translate import _
from mail.mail_message import to_email
import tools


class mail_compose_message(osv.osv_memory):
    _inherit = 'mail.compose.message'

    _columns = {
        'force_html': fields.boolean('Use Body Rich/HTML ?', help="If checked Body Rich/HTML, While sending the mail Body HTML will be given prority. Also while reply mail Body Rich/HTML is checked HTML reply will be given prority. If not not checked plain mail will be sent."),
    }

    _defaults = {
        "force_html": True
    }

    def send_mail(self, cr, uid, ids, context=None):
        '''
        Overloaded Process:Process Wizard contents and proceed with sending the
        corresponding email(s), rendering any template patterns on the fly if
        needed.
        This is to Enforce the Send Mail Process to Give Prority for HTML Body
        While Sending Mail. It Replce While Old Method for the Wizard.
        '''
        if context is None:
            context = {}
        mail_message = self.pool.get('mail.message')
        for mail in self.browse(cr, uid, ids, context=context):
            attachment = {}
            for attach in mail.attachment_ids:
                attachment[attach.datas_fname] = attach.datas and attach.datas.decode('base64')
            references = None
            headers = {}
            mail_subtype = mail.subtype
            body = mail.body_html if mail.subtype == 'html' else mail.body_text
            if mail.force_html and mail.body_html and mail.body_html.strip():
                body, mail_subtype = mail.body_html, 'html'
            else:
                body, mail_subtype = mail.body_text, 'plain'

            # Reply Email
            if context.get('mail.compose.message.mode') == 'reply' and mail.message_id:
                references = (mail.references or '') + " " + mail.message_id
                headers['In-Reply-To'] = mail.message_id

            if context.get('mail.compose.message.mode') == 'mass_mail':
                # Mass mailing: must render the template patterns
                if context.get('active_ids') and context.get('active_model'):
                    active_ids = context['active_ids']
                    active_model = context['active_model']
                else:
                    active_model = mail.model
                    active_model_pool = self.pool.get(active_model)
                    active_ids = active_model_pool.search(cr, uid, ast.literal_eval(mail.filter_id.domain), context=ast.literal_eval(mail.filter_id.context))

                for active_id in active_ids:
                    render_context = self._prepare_render_template_context(cr, uid, active_model, active_id, context)
                    subject = self.render_template(cr, uid, mail.subject, active_model, active_id, render_context)
                    rendered_body = self.render_template(cr, uid, body, active_model, active_id, render_context)
                    email_from = self.render_template(cr, uid, mail.email_from, active_model, active_id, render_context)
                    email_to = self.render_template(cr, uid, mail.email_to, active_model, active_id, render_context)
                    email_cc = self.render_template(cr, uid, mail.email_cc, active_model, active_id, render_context)
                    email_bcc = self.render_template(cr, uid, mail.email_bcc, active_model, active_id, render_context)
                    reply_to = self.render_template(cr, uid, mail.reply_to, active_model, active_id, render_context)

                    # in mass-mailing mode we only schedule the mail for sending, it will be
                    # processed as soon as the mail scheduler runs.
                    mail_message.schedule_with_attach(cr, uid, email_from, to_email(email_to), subject, rendered_body,
                        model=mail.model, email_cc=to_email(email_cc), email_bcc=to_email(email_bcc), reply_to=reply_to,
                        attachments=attachment, references=references, res_id=active_id,
                        subtype=mail_subtype, headers=headers, context=context)
            else:
                # normal mode - no mass-mailing
                msg_id = mail_message.schedule_with_attach(cr, uid, mail.email_from, to_email(mail.email_to), mail.subject, body,
                    model=mail.model, email_cc=to_email(mail.email_cc), email_bcc=to_email(mail.email_bcc), reply_to=mail.reply_to,
                    attachments=attachment, references=references, res_id=int(mail.res_id),
                    subtype=mail_subtype, headers=headers, context=context)
                # in normal mode, we send the email immediately, as the user expects us to (delay should be sufficiently small)
                mail_message.send(cr, uid, [msg_id], context=context)

        return {'type': 'ir.actions.act_window_close'}

    def get_message_data(self, cr, uid, message_id, context=None):
        """
        Over-rides the mail messsage reply mail default_get to give prority to the HTML Reply.
        """
        result = super(mail_compose_message, self).get_message_data(cr, uid, message_id, context)
        mail_message = self.pool.get('mail.message')
        result.update({"subtype": "plain","force_html": False})
        if message_id:
            message_data = mail_message.browse(cr, uid, message_id, context)
            if message_data.subtype == "html":
                current_user = self.pool.get('res.users').browse(cr, uid, uid, context)
                sender = _('%(sender_name)s wrote:') % {'sender_name': tools.ustr(message_data.email_from or _('You'))}
                sent_date = _('On %(date)s, ') % {'date': message_data.date} if message_data.date else ''
                body = message_data.body_html or current_user.signature or ''
                quoted_body = '> %s' % tools.ustr(body.replace('\n', "\n> ") or '')

                body = '\n'.join(["\n", (sent_date + sender), quoted_body])
                body += "\n" + (current_user.signature or '')
                result.update({"subtype": "html",
                               "force_html": True,
                               "body_html": body})
        return result
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
