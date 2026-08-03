import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StockEntry_model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(blank=True, max_length=255)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stock_entries', to=settings.AUTH_USER_MODEL)),
                ('stock_movement', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stock_entry', to='inventory.stockmovement_model')),
            ],
            options={
                'db_table': 'core_stock_entry',
            },
        ),
    ]
