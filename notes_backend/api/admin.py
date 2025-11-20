from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "is_archived", "updated_at")
    search_fields = ("title", "content")
    list_filter = ("is_archived",)
