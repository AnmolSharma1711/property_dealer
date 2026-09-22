from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ('properties', '0006_property_updated_at_chat_chatmessage_propertyhistory_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chats', to='auth.user'),
        ),
        migrations.AddField(
            model_name='chat',
            name='visitor_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='chat',
            name='visitor_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='chat',
            name='visitor_phone',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name='chat',
            name='access_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='sender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user'),
        ),
    ]