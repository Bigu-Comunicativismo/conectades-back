from rest_framework import serializers
from .models import Doacao


class DoacaoSerializer(serializers.ModelSerializer):
    doador_id = serializers.IntegerField(write_only=True, help_text="ID do doador (preenchido automaticamente)")
    campanha_id = serializers.IntegerField(write_only=True, help_text="ID da campanha")

    class Meta:
        model = Doacao
        fields = ['id', 'campanha', 'campanha_id', 'doador', 'doador_id', 'tipo', 'descricao', 'data_doacao']
        read_only_fields = ['id', 'campanha', 'doador', 'data_doacao']

    def create(self, validated_data):
        doador_id = validated_data.pop('doador_id')
        campanha_id = validated_data.pop('campanha_id')

        validated_data['doador_id'] = doador_id
        validated_data['campanha_id'] = campanha_id

        return Doacao.objects.create(**validated_data)







