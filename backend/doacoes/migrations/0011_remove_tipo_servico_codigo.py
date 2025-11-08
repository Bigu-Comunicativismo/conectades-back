from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doacoes', '0010_remove_doacaoindependente_extra_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tiposervico',
            name='codigo',
        ),
    ]

