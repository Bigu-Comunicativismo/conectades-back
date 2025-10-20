# Remove UsuarioExterno model (not used in the system)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campanhas', '0003_refactor_contribuicao'),
    ]

    operations = [
        # Remover campo usuario_externo de Campanha
        migrations.RemoveField(
            model_name='campanha',
            name='usuario_externo',
        ),
        
        # Deletar model UsuarioExterno
        migrations.DeleteModel(
            name='UsuarioExterno',
        ),
    ]

