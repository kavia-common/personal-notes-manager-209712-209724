from django.db import models
from django.conf import settings


class Note(models.Model):
    """
    Note model tied to a specific user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
        help_text="Owner of the note",
    )
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ["-updated_at"]  # Default ordering by updated_at desc
        indexes = [
            models.Index(fields=["user", "is_archived"]),
            models.Index(fields=["updated_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} (user={self.user_id})"
