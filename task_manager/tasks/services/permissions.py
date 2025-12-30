from task_manager.task.models import TaskMembership as TM


ROLE_PERMISSIONS = {
    'admin': {
        'change_state',
        'edit_task',
        'assign_users',
        'delete_task',
    },
    'executor': {
        'change_state'
    },
    'viewer': set(),
}


def has_permission(user, task, permission):
    record = TM.objects.get(user=user, task=task)
    return permission in ROLE_PERMISSIONS[record.role]
