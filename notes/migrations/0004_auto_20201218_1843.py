# Generated by Django 3.1.2 on 2020-12-18 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0003_auto_20201218_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='note_text',
            field=models.TextField(),
        ),
    ]
