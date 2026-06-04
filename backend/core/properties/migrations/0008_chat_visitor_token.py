# Generated for visitor-token chat access control.

import secrets

from django.db import migrations, models

import properties.models


def populate_visitor_tokens(apps, schema_editor):
    Chat = apps.get_model('properties', 'Chat')
    used_tokens = set(
        Chat.objects.exclude(visitor_token__isnull=True)
        .exclude(visitor_token='')
        .values_list('visitor_token', flat=True)
    )

    for chat in Chat.objects.filter(models.Q(visitor_token__isnull=True) | models.Q(visitor_token='')):
        token = secrets.token_urlsafe(32)
        while token in used_tokens:
            token = secrets.token_urlsafe(32)
        chat.visitor_token = token
        chat.save(update_fields=['visitor_token'])
        used_tokens.add(token)


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0007_chat_visitor_email_chat_visitor_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='visitor_token',
            field=models.CharField(blank=True, editable=False, max_length=64, null=True, unique=True),
        ),
        migrations.RunPython(populate_visitor_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='chat',
            name='visitor_token',
            field=models.CharField(blank=True, default=properties.models.generate_visitor_token, editable=False, max_length=64, null=True, unique=True),
        ),
    ]
