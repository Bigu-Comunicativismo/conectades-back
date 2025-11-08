from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doacoes', '0009_delete_tipodoacao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='agendamentos_confirmados',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='agendamentos_realizados',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='duracao_atendimento',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='dias_semana',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='frequencia_semanal',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='horario_fim',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='horario_inicio',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='observacoes',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='quantidade_pessoas',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='requisitos',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='whatsapp',
        ),
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='email_contato',
        ),
    ]

