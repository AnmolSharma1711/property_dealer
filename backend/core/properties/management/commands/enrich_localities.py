"""
Django management command to enrich localities with AI analysis.

Usage:
    python manage.py enrich_localities              # Enrich all missing profiles
    python manage.py enrich_localities --id=5       # Enrich specific locality
    python manage.py enrich_localities --all        # Force re-enrich all
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
import threading
from properties.models import Locality
from properties.tasks import enrich_locality_pipeline


class Command(BaseCommand):
    help = 'Start AI analysis for localities (runs in background threads)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=int,
            help='Enrich specific locality by ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Re-enrich all localities (including those already analyzed)',
        )

    def handle(self, *args, **options):
        if options['id']:
            # Enrich specific locality
            try:
                locality = Locality.objects.get(id=options['id'])
                self.stdout.write(f"Starting AI analysis for: {locality.name} (ID: {locality.id})")
                thread = threading.Thread(target=enrich_locality_pipeline, args=(locality.id,), daemon=True)
                thread.start()
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Background thread started (will complete in 2-5 minutes)")
                )
            except Locality.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"✗ Locality with ID {options['id']} not found")
                )

        elif options['all']:
            # Re-enrich all localities
            localities = Locality.objects.all()
            count = localities.count()
            self.stdout.write(f"Starting AI analysis for {count} localities...")
            
            for locality in localities:
                thread = threading.Thread(target=enrich_locality_pipeline, args=(locality.id,), daemon=True)
                thread.start()
                self.stdout.write(f"  → {locality.name}: thread started")
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Started {count} background threads (will complete over next 2-5 minutes each)")
            )

        else:
            # Enrich localities without profiles
            localities = Locality.objects.filter(profile__isnull=True)
            count = localities.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.SUCCESS("✓ All localities already enriched!")
                )
                return
            
            self.stdout.write(f"Starting AI analysis for {count} localities without analysis...")
            
            for locality in localities:
                thread = threading.Thread(target=enrich_locality_pipeline, args=(locality.id,), daemon=True)
                thread.start()
                self.stdout.write(f"  → {locality.name} (ID: {locality.id}): thread started")
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Started {count} background threads (will complete over next 2-5 minutes each)")
            )
