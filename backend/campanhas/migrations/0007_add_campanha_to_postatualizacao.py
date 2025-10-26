# Add campanha field to PostAtualizacao

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campanhas', '0006_campanha_beneficiaria'),
    ]

    operations = [
        # Remover ManyToMany de Campanha.atualizacoes
        migrations.RemoveField(
            model_name='campanha',
            name='atualizacoes',
        ),
        
        # Adicionar ForeignKey em PostAtualizacao
        migrations.AddField(
            model_name='postatualizacao',
            name='campanha',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='posts_atualizacao',
                to='campanhas.campanha',
                verbose_name='Campanha',
                help_text='Campanha à qual este post pertence',
                null=True  # Temporariamente nullable
            ),
        ),
        
        # Deletar posts órfãos
        migrations.RunSQL(
            sql='DELETE FROM campanhas_postatualizacao;',
            reverse_sql='',
        ),
        
        # Tornar campo obrigatório
        migrations.AlterField(
            model_name='postatualizacao',
            name='campanha',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='posts_atualizacao',
                to='campanhas.campanha',
                verbose_name='Campanha',
                help_text='Campanha à qual este post pertence'
            ),
        ),
    ]

