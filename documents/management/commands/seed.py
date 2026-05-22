"""
documents/management/commands/seed.py

Creates a default superuser and sample documents for demo/testing purposes.
Usage: python manage.py seed
"""

import io
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from documents.models import Document, Category


SAMPLE_DOCUMENTS = [
    {
        "title": "2024-yil 1-son Kafedra majlisi protokoli",
        "category": Category.PROTOKOL,
        "description": "Kafedra yillik ish rejasini muhokama qilish bo'yicha o'tkazilgan majlis protokoli.",
    },
    {
        "title": "2024-2025 o'quv yili ish rejasi",
        "category": Category.REJE,
        "description": "Kafedra 2024-2025 o'quv yili uchun tuzilgan yillik ish rejasi.",
    },
    {
        "title": "Ilmiy-tadqiqot ishlari bo'yicha qaror",
        "category": Category.QARAR,
        "description": "Kafedra ilmiy-tadqiqot ishlarini rivojlantirish bo'yicha qabul qilingan qaror.",
    },
    {
        "title": "O'quv yuklamalarini taqsimlash to'g'risida buyruq",
        "category": Category.BUYRUQ,
        "description": "Professor-o'qituvchilar o'rtasida o'quv yuklamalarini taqsimlash haqidagi buyruq.",
    },
    {
        "title": "2023-2024 o'quv yili yakuniy hisoboti",
        "category": Category.HISOBOT,
        "description": "O'tgan o'quv yili bo'yicha kafedra faoliyatining yakuniy hisoboti.",
    },
    {
        "title": "Informatika fanidan o'quv dasturi",
        "category": Category.DASTUR,
        "description": "Informatika fani bo'yicha yangilangan o'quv dasturi va sillabus.",
    },
    {
        "title": "Xalqaro hamkorlik to'g'risida ma'lumotnoma",
        "category": Category.BOSHQA,
        "description": "Xorijiy universitetlar bilan hamkorlik aloqalari haqidagi ma'lumotnoma.",
    },
]


class Command(BaseCommand):
    help = "Seeds the database with a default admin user and sample documents."

    def handle(self, *args, **options):
        self.stdout.write("🌱  Seeding database...")

        # --- Superuser ---
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@kafedra.uz",
                password="admin1234",
            )
            self.stdout.write(self.style.SUCCESS("  ✔ Superuser created: admin / admin1234"))
        else:
            admin = User.objects.get(username="admin")
            self.stdout.write("  – Superuser 'admin' already exists, skipping.")

        # --- Sample documents ---
        created_count = 0
        for data in SAMPLE_DOCUMENTS:
            if Document.objects.filter(title=data["title"]).exists():
                self.stdout.write(f"  – Skipping existing: {data['title']}")
                continue

            # Create a minimal placeholder text file so the FileField is not empty
            filename = data["title"][:40].replace(" ", "_").replace("'", "") + ".txt"
            file_content = ContentFile(
                f"[Demo fayl]\n\nSarlavha: {data['title']}\nKategoriya: {data['category']}\n\n{data['description']}\n".encode("utf-8"),
                name=filename,
            )

            Document.objects.create(
                title=data["title"],
                category=data["category"],
                description=data["description"],
                uploaded_by=admin,
                file=file_content,
            )
            created_count += 1
            self.stdout.write(f"  ✔ Created: {data['title']}")

        self.stdout.write(self.style.SUCCESS(
            f"\n✅  Done. {created_count} document(s) created."
        ))