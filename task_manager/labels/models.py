from django.db import models
from django.db.models.deletion import ProtectedError
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Label(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.tasks.exists():
            raise ProtectedError(
                _('Cannot delete task because they are used in other objects.'),
                self.tasks.all(),
            )
        return super().delete(*args, **kwargs)
