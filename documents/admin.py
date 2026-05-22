"""
documents/admin.py
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display  = ("title", "category", "uploaded_by", "uploaded_at", "has_ai_summary")
    list_filter   = ("category", "uploaded_at")
    search_fields = ("title", "description")
    readonly_fields = ("ai_summary", "ai_analyzed_at", "uploaded_at", "updated_at")

    fieldsets = (
        (_("Asosiy ma'lumotlar"), {
            "fields": ("title", "category", "description", "file", "uploaded_by"),
        }),
        (_("AI tahlili"), {
            "fields": ("ai_summary", "ai_analyzed_at"),
            "classes": ("collapse",),
        }),
        (_("Vaqt belgilari"), {
            "fields": ("uploaded_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(boolean=True, description=_("AI tahlili"))
    def has_ai_summary(self, obj):
        return bool(obj.ai_summary)
