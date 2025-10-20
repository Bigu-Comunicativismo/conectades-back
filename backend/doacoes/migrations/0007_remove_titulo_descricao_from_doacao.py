# Remove titulo and descricao from Doacao (unnecessary fields)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doacoes', '0006_add_item_campanha_to_doacao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doacao',
            name='titulo',
        ),
        migrations.RemoveField(
            model_name='doacao',
            name='descricao',
        ),
    ]

