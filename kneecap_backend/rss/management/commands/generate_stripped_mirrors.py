from django.core.management.base import BaseCommand
from rss.models import FeedMirror, StrippedMirror

class Command(BaseCommand):
    help = 'Generates stripped mirrors for all feed mirrors'

    def handle(self, *args, **options):
        feed_mirrors = FeedMirror.objects.all()
        created_count = 0
        updated_count = 0

        for feed_mirror in feed_mirrors:
            stripped_mirror, created = StrippedMirror.objects.get_or_create(
                feed_mirror=feed_mirror,
                defaults={'stripped_content': ''}
            )
            
            # Generate/update the stripped content
            stripped_mirror.update()

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} and updated {updated_count} stripped mirrors'
            )
        ) 