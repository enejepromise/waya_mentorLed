from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_parent_realtime(user, message, chore_id=None):
    """
    Sends a real-time WebSocket notification to the parent user.

    :param user: The Django user instance (must be authenticated).
    :param message: The message content.
    :param chore_id: Optional chore ID to include in the notification.
    """
    if not user or not user.is_authenticated:
        return

    channel_layer = get_channel_layer()
    content = {
        "title": "Chore Completed" if chore_id else "Notification",
        "message": message,
    }

    if chore_id:
        content["choreId"] = str(chore_id)

    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "content": content
        }
    )

def send_notification(user, message):
    """
    A generic notification function for any type of real-time user message.
    """
    notify_parent_realtime(user, message)
