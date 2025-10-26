# Add item_campanha field to Doacao

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('doacoes', '0005_remove_doacao_valor_estimado'),
        ('campanhas', '0005_rename_item_to_itemcampanha'),
    ]

    operations = [
        # Adicionar campo item_campanha em Doacao
        migrations.AddField(
            model_name='doacao',
            name='item_campanha',
            field=models.ForeignKey(
                blank=True,
                help_text='Item específico da campanha que está sendo contribuído (opcional)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='doacoes',
                to='campanhas.itemcampanha',
                verbose_name='Item da Campanha'
            ),
        ),
    ]

