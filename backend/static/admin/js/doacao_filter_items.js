/**
 * Filtra os itens disponíveis baseado na campanha selecionada
 * Atualiza dinamicamente o campo item_campanha quando campanha muda
 */
(function($) {
    'use strict';
    
    $(document).ready(function() {
        const campanhaField = $('#id_campanha');
        const itemCampanhaField = $('#id_item_campanha');
        
        if (!campanhaField.length || !itemCampanhaField.length) {
            return; // Campos não existem nesta página
        }
        
        console.log('🔧 Filtro de itens por campanha carregado');
        
        // Função para atualizar os itens disponíveis
        function updateItemOptions() {
            const campanhaId = campanhaField.val();
            
            console.log('📋 Campanha selecionada:', campanhaId);
            
            if (!campanhaId) {
                // Sem campanha selecionada: limpar itens
                itemCampanhaField.empty();
                itemCampanhaField.append('<option value="">⚠️ Selecione uma campanha primeiro</option>');
                itemCampanhaField.prop('disabled', true);
                return;
            }
            
            // Desabilitar temporariamente
            itemCampanhaField.prop('disabled', true);
            itemCampanhaField.empty();
            itemCampanhaField.append('<option value="">Carregando...</option>');
            
            // Buscar itens da campanha via API
            $.getJSON(`/api/campanhas/${campanhaId}/itens/`)
                .done(function(itens) {
                    console.log(`✅ ${itens.length} itens encontrados para campanha ${campanhaId}`);
                    
                    // Limpar select
                    itemCampanhaField.empty();
                    itemCampanhaField.append('<option value="">---------</option>');
                    
                    if (itens.length > 0) {
                        // Popular com itens da campanha
                        itens.forEach(function(item) {
                            const percentual = item.percentual_atingido.toFixed(0);
                            const displayText = `${item.nome} (${item.quantidade_contribuida}/${item.quantidade_solicitada} ${item.unidade}) [${percentual}%]`;
                            
                            itemCampanhaField.append(
                                $('<option></option>')
                                    .val(item.id)
                                    .text(displayText)
                            );
                        });
                        itemCampanhaField.prop('disabled', false);
                    } else {
                        itemCampanhaField.append('<option value="">⚠️ Esta campanha não tem itens cadastrados</option>');
                        itemCampanhaField.prop('disabled', true);
                    }
                })
                .fail(function(xhr, status, error) {
                    console.error('❌ Erro ao buscar itens:', error);
                    itemCampanhaField.empty();
                    itemCampanhaField.append('<option value="">Erro ao carregar itens</option>');
                    itemCampanhaField.prop('disabled', true);
                });
        }
        
        // Atualizar quando campanha mudar
        campanhaField.on('change', function() {
            console.log('🔄 Campanha alterada, atualizando itens...');
            updateItemOptions();
        });
        
        // Atualizar ao carregar a página (se já tiver campanha selecionada)
        if (campanhaField.val()) {
            console.log('🔄 Página carregada com campanha selecionada, atualizando itens...');
            updateItemOptions();
        } else {
            itemCampanhaField.empty();
            itemCampanhaField.append('<option value="">⚠️ Selecione uma campanha primeiro</option>');
            itemCampanhaField.prop('disabled', true);
        }
    });
})(django.jQuery);

