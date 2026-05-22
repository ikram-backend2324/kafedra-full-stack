"""
documents/views.py

Views:
  - DashboardView  — lists all documents with search + category filter
  - UploadView     — handles document upload
  - DocumentDetail — single document detail
  - AnalyzeView    — triggers AI analysis via OpenRouter Gemini
  - DeleteView     — soft-deletes a document
"""

import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import DocumentUploadForm
from .models import Category, Document
from .utils import analyze_document


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardView(LoginRequiredMixin, ListView):
    model = Document
    template_name = "dashboard.html"
    context_object_name = "documents"
    paginate_by = 12

    def get_queryset(self):
        qs = Document.objects.select_related("uploaded_by").all()

        # Category filter
        category = self.request.GET.get("category", "")
        if category:
            qs = qs.filter(category=category)

        # Text search across title and description
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Stats for summary cards
        ctx["total_docs"]    = Document.objects.count()
        ctx["ai_analyzed"]   = Document.objects.exclude(ai_summary="").count()
        ctx["categories"]    = Category.choices
        ctx["current_cat"]   = self.request.GET.get("category", "")
        ctx["search_query"]  = self.request.GET.get("q", "")

        # Per-category counts for the sidebar widget
        cat_counts = (
            Document.objects.values("category")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        ctx["category_counts"] = {item["category"]: item["count"] for item in cat_counts}

        return ctx


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------
class UploadView(LoginRequiredMixin, View):
    template_name = "documents/upload.html"

    def get(self, request):
        return render(request, self.template_name, {"form": DocumentUploadForm()})

    def post(self, request):
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, _("Hujjat muvaffaqiyatli yuklandi."))
            return redirect("document_detail", pk=doc.pk)
        return render(request, self.template_name, {"form": form})


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------
class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = "documents/detail.html"
    context_object_name = "doc"


# ---------------------------------------------------------------------------
# AI Analysis (AJAX-friendly)
# ---------------------------------------------------------------------------
@method_decorator(login_required, name="dispatch")
class AnalyzeView(View):
    """
    POST /documents/<pk>/analyze/
    Calls OpenRouter Gemini with the document metadata and saves the summary.
    Returns JSON so the frontend can show the result without a full page reload.
    """

    def post(self, request, pk):
        doc = get_object_or_404(Document, pk=pk)

        # Detect active UI language for dynamic Gemini language instruction
        language_code = getattr(request, "LANGUAGE_CODE", "uz")

        summary = analyze_document(
            document_title=doc.title,
            document_description=doc.description,
            language_code=language_code,
        )

        # Persist the summary
        doc.ai_summary = summary
        doc.ai_analyzed_at = timezone.now()
        doc.save(update_fields=["ai_summary", "ai_analyzed_at"])

        # Support both AJAX and standard POST
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"summary": summary, "analyzed_at": doc.ai_analyzed_at.isoformat()})

        messages.success(request, _("AI tahlili muvaffaqiyatli yakunlandi."))
        return redirect("document_detail", pk=pk)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------
@login_required
def delete_document(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == "POST":
        doc.file.delete(save=False)   # remove file from disk
        doc.delete()
        messages.success(request, _("Hujjat o'chirildi."))
    return redirect("dashboard")
