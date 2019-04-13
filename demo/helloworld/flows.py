import os
from django.utils.translation import ugettext_lazy as _

from viewflow import flow, frontend, lock
from viewflow.base import this, Flow
from viewflow.flow import views as flow_views


from .models import HelloWorldProcess


@frontend.register
class HelloWorldFlow(Flow):
    """
    Hello world

    This process demonstrates hello world approval request flow.
    """
    process_class = HelloWorldProcess
    process_title = _('Ciao Mondo')
    process_description = _("Questo processo è relativo all'approvazine di un messaggio.")

    lock_impl = lock.select_for_update_lock

    summary_template = _("Messaggio al mondo: '{{ process.text }}'")

    start = (
        flow.Start(
            flow_views.CreateProcessView,
            fields=['text'],
            task_title=_('Nuovo messaggio'))
        .Permission(auto_create=True)
        .Next(this.approve)
    )

    approve = (
        flow.View(
            flow_views.UpdateProcessView, fields = ['approved'],
            task_title=_('Approvazione'),
            task_description=_(" E' richiesta l'approvazione {{ process.text }}	 "),
            task_result_summary=_("Il messaggio è stato: {{ process.approved|yesno:'Approved,Rejected' }}"))
        .Permission(auto_create=True)
        .Next(this.check_approve)
    )

    check_approve = (
        flow.If(
            cond=lambda act: act.process.approved,
            task_title=_('Verifica approvazione'),
        )
        .Then(this.send)
        .Else(this.end)
    )

    send = (
        flow.Handler(
            this.send_hello_world_request,
            task_title=_('Spedizione messaggio'),
        )
        .Next(this.end)
    )

    end = flow.End(
        task_title=_('End'),
    )

    def send_hello_world_request(self, activation):
        with open(os.devnull, "w") as world:
            world.write(activation.process.text)
