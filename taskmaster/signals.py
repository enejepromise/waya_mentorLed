# taskmaster/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from taskmaster.models import Chore, notify_parent_realtime

@receiver(post_save, sender=Chore)
def chore_status_change_handler(sender, instance, created, **kwargs):
    if not created:
        # Fetch the previous state from the database
        previous = sender.objects.filter(pk=instance.pk).first()
        if previous is None:
            return

        # If status just changed to completed, notify parent
        if previous.status != Chore.STATUS_COMPLETED and instance.status == Chore.STATUS_COMPLETED:
            message = f"{instance.assigned_to.username} completed '{instance.title}'"
            notify_parent_realtime(instance.parent, message, instance.id)
