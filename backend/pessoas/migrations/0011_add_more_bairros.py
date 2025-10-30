# Generated manually

from django.db import migrations


def add_bairros_recife(apps, schema_editor):
    """Adiciona mais bairros de Recife para melhor cobertura"""
    LocalizacaoInteresse = apps.get_model('pessoas', 'LocalizacaoInteresse')
    
    import unicodedata
    from django.utils.text import slugify
    
    # Bairros de Recife - RMR
    bairros_recife = [
        'Afogados',
        'Água Fria',
        'Alto do Mandu',
        'Apipucos',
        'Arruda',
        'Barro',
        'Beberibe',
        'Boa Vista',
        'Bomba do Hemetério',
        'Bongi',
        'Brasília Teimosa',
        'Brejo da Guabiraba',
        'Brejo de Beberibe',
        'Cabanga',
        'Cacote',
        'Caiara',
        'Cajueiro',
        'Campina do Barreto',
        'Campo Grande',
        'Caçote',
        'Cidade Universitária',
        'Coelhos',
        'Cohab',
        'Cordeiro',
        'Coque',
        'Curado',
        'Derby',
        'Dois Irmãos',
        'Dois Unidos',
        'Encruzilhada',
        'Espinheiro',
        'Estância',
        'Fundão',
        'Guabiraba',
        'Hipódromo',
        'Ibura',
        'Ilha do Leite',
        'Ilha do Retiro',
        'Ilha Joana Bezerra',
        'Ipsep',
        'Iputinga',
        'Jaqueira',
        'Jardim São Paulo',
        'Jiquiá',
        'Jordão',
        'Linha do Tiro',
        'Macaxeira',
        'Madalena',
        'Mangabeira',
        'Mangueira',
        'Monteiro',
        'Morro da Conceição',
        'Mustardinha',
        'Parnamirim',
        'Passarinho',
        'Pau-Ferro',
        'Peixinhos',
        'Ponto de Parada',
        'Porto da Madeira',
        'Prado',
        'Recife',
        'Rosarinho',
        'San Martin',
        'Sancho',
        'Santa Luzia',
        'Santana',
        'São José',
        'Sitio dos Pintos',
        'Sítio Grande',
        'Socorro',
        'Tamarineira',
        'Torre',
        'Torrões',
        'Torreão',
        'Totó',
        'Ur-01 - Ibura',
        'Ur-02 - Ibura',
        'Ur-03 - Ibura',
        'Ur-04 - Ibura',
        'Ur-05 - Mustardinha',
        'Ur-06 - Jordão',
        'Ur-07 - Barro',
        'Ur-08 - Tejipió',
        'Ur-09 - Coqueiral',
        'Ur-10 - Tejipió',
        'Ur-11 - Caçote',
        'Várzea',
        'Vasco da Gama',
        'Zumbi',
    ]
    
    # Bairros de Olinda
    bairros_olinda = [
        'Águas Compridas',
        'Alto da Bondade',
        'Alto da Conquista',
        'Alto da Mina',
        'Alto do Sol Nascente',
        'Amador',
        'Amparo',
        'Bairro Novo',
        'Bultrins',
        'Caixa D\'Água',
        'Campo do América',
        'Carmo',
        'Casa Caiada',
        'Cidade Tabajara',
        'Fragoso',
        'Guadalupe',
        'Jardim Atlântico',
        'Jardim Brasil',
        'Monte',
        'Mouraria',
        'Ouro Preto',
        'Passarinho',
        'Peixinhos',
        'Pissarrão',
        'Prado',
        'Rio Doce',
        'Santa Tereza',
        'São Benedito',
        'Sapucaia',
        'Sítio Histórico',
        'Tabajara',
        'Varadouro',
        'Vila Popular',
    ]
    
    # Bairros de Jaboatão dos Guararapes
    bairros_jaboatao = [
        'Barra de Jangada',
        'Candeias',
        'Cavaleiro',
        'Comportas',
        'Curado',
        'Jaboatão Centro',
        'Jardim Jordão',
        'Muribeca',
        'Parneras',
        'Piedade',
        'Prazeres',
        'Socorro',
    ]
    
    # Adicionar bairros de Recife
    ordem = 100  # Começar de 100 para não conflitar com dados existentes
    for bairro_nome in sorted(bairros_recife):
        codigo_base = slugify(unicodedata.normalize('NFKD', bairro_nome).encode('ascii', 'ignore').decode('ascii'))
        codigo = f"{codigo_base}-bairro"[:100]
        
        LocalizacaoInteresse.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nome': bairro_nome,
                'tipo': 'bairro',
                'cidade': 'Recife',
                'estado': 'PE',
                'ordem': ordem,
                'ativo': True
            }
        )
        ordem += 1
    
    # Adicionar bairros de Olinda
    for bairro_nome in sorted(bairros_olinda):
        codigo_base = slugify(unicodedata.normalize('NFKD', bairro_nome).encode('ascii', 'ignore').decode('ascii'))
        codigo = f"{codigo_base}-bairro"[:100]
        
        LocalizacaoInteresse.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nome': bairro_nome,
                'tipo': 'bairro',
                'cidade': 'Olinda',
                'estado': 'PE',
                'ordem': ordem,
                'ativo': True
            }
        )
        ordem += 1
    
    # Adicionar bairros de Jaboatão dos Guararapes
    for bairro_nome in sorted(bairros_jaboatao):
        codigo_base = slugify(unicodedata.normalize('NFKD', bairro_nome).encode('ascii', 'ignore').decode('ascii'))
        codigo = f"{codigo_base}-bairro"[:100]
        
        LocalizacaoInteresse.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nome': bairro_nome,
                'tipo': 'bairro',
                'cidade': 'Jaboatão dos Guararapes',
                'estado': 'PE',
                'ordem': ordem,
                'ativo': True
            }
        )
        ordem += 1


def reverse_add_bairros(apps, schema_editor):
    """Remove os bairros adicionados"""
    LocalizacaoInteresse = apps.get_model('pessoas', 'LocalizacaoInteresse')
    # Remove apenas os bairros adicionados nesta migration (ordem >= 100)
    LocalizacaoInteresse.objects.filter(tipo='bairro', ordem__gte=100).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0010_add_token_field'),
    ]

    operations = [
        migrations.RunPython(add_bairros_recife, reverse_add_bairros),
    ]

