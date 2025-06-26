from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_parent_realtime(user, message, task_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "content": {
                "title": "Task Completed",
                "message": message,
                "taskId": str(task_id),
            }
        }
    )
