# Generated by Django 4.1.13 on 2024-09-27 16:21

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='YourModel',
        ),
        migrations.AlterModelOptions(
            name='questionanswer',
            options={'ordering': ['question'], 'verbose_name': 'Question Answer', 'verbose_name_plural': 'Question Answers'},
        ),
        migrations.AddField(
            model_name='userinteraction',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='questionanswer',
            name='question',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.MaxLengthValidator(255)]),
        ),
        migrations.AlterField(
            model_name='socialtoken',
            name='token_secret',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
