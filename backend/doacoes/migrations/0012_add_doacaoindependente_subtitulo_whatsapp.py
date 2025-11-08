from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doacoes', '0011_remove_tipo_servico_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='doacaoindependente',
            name='subtitulo',
            field=models.CharField(
                max_length=200,
                blank=True,
                null=True,
                verbose_name='Subtítulo',
                help_text='Subtítulo do serviço (opcional)'
            ),
        ),
        migrations.AddField(
            model_name='doacaoindependente',
            name='whatsapp',
            field=models.CharField(
                max_length=20,
                blank=True,
                null=True,
                verbose_name='WhatsApp',
                help_text='Número de contato via WhatsApp'
            ),
        ),
    ]

