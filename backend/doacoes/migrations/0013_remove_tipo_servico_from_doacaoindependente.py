from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doacoes', '0012_add_doacaoindependente_subtitulo_whatsapp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doacaoindependente',
            name='tipo_servico',
        ),
        migrations.AlterField(
            model_name='doacaoindependente',
            name='categorias',
            field=models.ManyToManyField(
                help_text='Categorias relacionadas ao serviço',
                to='doacoes.tiposervico',
                verbose_name='Categorias'
            ),
        ),
    ]

