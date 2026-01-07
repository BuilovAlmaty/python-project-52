from task_manager.tasks.models import TaskMembership as TM

ROLE_PERMISSIONS = {
    'admin': {
        'change_state',
        'edit_task',
        'delete_task',
    },
    'executor': {
        'change_state',
        'edit_task',
    },
    'creator': {
        'change_state',
        'edit_task',
        'delete_task',
    },
    'viewer': set(),
}


def has_permission(user, task, permission):
    record = TM.objects.filter(user=user, task=task).first()
    if not record:
        return False
    return permission in ROLE_PERMISSIONS[record.role]
