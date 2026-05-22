"""
documents/models.py

Core data model for the Electronic Department Document Management System.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.TextChoices):
    """Document categories used across the department."""
    PROTOKOL   = "protokol",   _("Protokol")          # Meeting minutes
    REJE       = "reje",       _("Reje")               # Plans / schedules
    QARAR      = "qarar",      _("Qarar")              # Decisions / resolutions
    BUYRUQ     = "buyruq",     _("Buyruq")             # Orders
    HISOBOT    = "hisobot",    _("Hisobot")            # Reports
    DASTUR     = "dastur",     _("Dastur")             # Programs / curricula
    BOSHQA     = "boshqa",     _("Boshqa")             # Other


class Document(models.Model):
    """Represents a single uploaded department document."""

    title = models.CharField(
        max_length=255,
        verbose_name=_("Sarlavha"),
        help_text=_("Hujjat sarlavhasi yoki qisqa tavsifi"),
    )

    file = models.FileField(
        upload_to="documents/%Y/%m/",
        verbose_name=_("Fayl"),
        help_text=_("PDF, DOCX yoki boshqa hujjat fayli"),
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.BOSHQA,
        verbose_name=_("Kategoriya"),
        db_index=True,
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Tavsif"),
        help_text=_("Ixtiyoriy qo'shimcha tavsif"),
    )

    uploaded_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Yuklagan foydalanuvchi"),
        related_name="documents",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Yuklangan vaqt"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Yangilangan vaqt"),
    )

    # -----------------------------------------------------------------------
    # AI-generated fields
    # -----------------------------------------------------------------------
    ai_summary = models.TextField(
        blank=True,
        verbose_name=_("AI tahlili"),
        help_text=_("Gemini tomonidan yaratilgan avtomatik xulosa"),
    )

    ai_analyzed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("AI tahlil vaqti"),
    )

    class Meta:
        verbose_name = _("Hujjat")
        verbose_name_plural = _("Hujjatlar")
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.get_category_display()} — {self.title}"

    @property
    def filename(self):
        """Return just the file name without the full upload path."""
        return self.file.name.split("/")[-1] if self.file else ""

    @property
    def file_extension(self):
        """Return the file extension (lowercase), e.g. 'pdf'."""
        if self.file:
            parts = self.filename.rsplit(".", 1)
            return parts[-1].lower() if len(parts) > 1 else ""
        return ""
