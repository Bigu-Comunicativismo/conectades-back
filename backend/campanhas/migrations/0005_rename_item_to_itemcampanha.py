# Refactor Item to ItemCampanha (delete and recreate)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campanhas', '0004_remove_usuario_externo'),
    ]

    operations = [
        # Remover o ManyToMany de Campanha.solicitacoes primeiro
        migrations.RemoveField(
            model_name='campanha',
            name='solicitacoes',
        ),
        
        # Deletar modelo Item antigo
        migrations.DeleteModel(
            name='Item',
        ),
        
        # Criar novo modelo ItemCampanha
        migrations.CreateModel(
            name='ItemCampanha',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(help_text="Nome do item solicitado (ex: 'Arroz tipo 1', 'Feijão carioca')", max_length=200, verbose_name='Nome do Item')),
                ('quantidade_solicitada', models.PositiveIntegerField(help_text='Quantidade total solicitada do item', verbose_name='Quantidade Solicitada')),
                ('quantidade_contribuida', models.PositiveIntegerField(default=0, help_text='Quantidade já contribuída do item', verbose_name='Quantidade Contribuída')),
                ('unidade', models.CharField(default='unidade', help_text='Unidade de medida (kg, litros, unidades, pacotes, etc.)', max_length=50, verbose_name='Unidade')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('campanha', models.ForeignKey(help_text='Campanha à qual este item pertence', on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='campanhas.campanha', verbose_name='Campanha')),
            ],
            options={
                'verbose_name': 'Item da Campanha',
                'verbose_name_plural': 'Itens das Campanhas',
                'ordering': ['campanha', 'nome'],
                'unique_together': {('campanha', 'nome')},
            },
        ),
    ]

