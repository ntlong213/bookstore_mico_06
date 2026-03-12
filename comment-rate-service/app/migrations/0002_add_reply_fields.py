from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentrate',
            name='replied_by',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='commentrate',
            name='replied_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
