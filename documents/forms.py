"""
documents/forms.py
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "category", "description", "file"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": (
                    "w-full px-4 py-2.5 rounded-lg border border-slate-200 "
                    "bg-white text-slate-800 placeholder-slate-400 "
                    "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
                    "transition duration-200"
                ),
                "placeholder": _("Hujjat sarlavhasini kiriting…"),
            }),
            "category": forms.Select(attrs={
                "class": (
                    "w-full px-4 py-2.5 rounded-lg border border-slate-200 "
                    "bg-white text-slate-800 "
                    "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
                    "transition duration-200"
                ),
            }),
            "description": forms.Textarea(attrs={
                "rows": 3,
                "class": (
                    "w-full px-4 py-2.5 rounded-lg border border-slate-200 "
                    "bg-white text-slate-800 placeholder-slate-400 "
                    "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
                    "transition duration-200 resize-none"
                ),
                "placeholder": _("Ixtiyoriy tavsif…"),
            }),
            "file": forms.FileInput(attrs={
                "class": (
                    "block w-full text-sm text-slate-500 "
                    "file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 "
                    "file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 "
                    "hover:file:bg-indigo-100 cursor-pointer"
                ),
                "accept": ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.odt",
            }),
        }
        labels = {
            "title":       _("Sarlavha"),
            "category":    _("Kategoriya"),
            "description": _("Tavsif"),
            "file":        _("Fayl"),
        }
