# Generated manually to refactor Contribuicao model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campanhas', '0002_auto_20251019_2257'),
        ('doacoes', '0005_remove_doacao_valor_estimado'),
    ]

    operations = [
        # Remover o campo contribuicoes do model Campanha
        migrations.RemoveField(
            model_name='campanha',
            name='contribuicoes',
        ),
        
        # Deletar modelo Contribuicao (será substituído por Doacao.item_campanha)
        migrations.DeleteModel(
            name='Contribuicao',
        ),
    ]

