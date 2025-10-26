#!/bin/bash

echo "=========================================="
echo "🔐 Script para copiar chave SSH para VPS"
echo "=========================================="
echo ""

# Solicitar informações do servidor
read -p "Digite o IP ou hostname do servidor VPS: " SERVER_IP
read -p "Digite o usuário SSH (geralmente 'root'): " SSH_USER
read -p "Digite a porta SSH (geralmente '22'): " SSH_PORT

SSH_PORT=${SSH_PORT:-22}
SSH_USER=${SSH_USER:-root}

echo ""
echo "📤 Copiando chave pública para $SSH_USER@$SERVER_IP:$SSH_PORT..."
echo ""

# Copiar a chave pública
ssh-copy-id -i ~/.ssh/id_rsa_conectades.pub -p $SSH_PORT $SSH_USER@$SERVER_IP

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Chave copiada com sucesso!"
    echo ""
    echo "🧪 Testando conexão..."
    echo ""
    
    # Testar conexão
    ssh -i ~/.ssh/id_rsa_conectades -p $SSH_PORT $SSH_USER@$SERVER_IP "echo '✅ Conexão SSH funcionando sem senha!'; exit"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "=========================================="
        echo "✅ TUDO CONFIGURADO COM SUCESSO!"
        echo "=========================================="
        echo ""
        echo "📋 Próximos passos:"
        echo ""
        echo "1. Configure os secrets no GitHub:"
        echo "   - DEV_SSH_HOST = $SERVER_IP"
        echo "   - DEV_SSH_USERNAME = $SSH_USER"
        echo "   - DEV_SSH_PORT = $SSH_PORT"
        echo "   - DEV_PROJECT_PATH = /var/www/conectades-dev"
        echo "   - DEV_SSH_PRIVATE_KEY = (conteúdo de ~/.ssh/id_rsa_conectades)"
        echo ""
        echo "2. Para copiar a chave privada, execute:"
        echo "   cat ~/.ssh/id_rsa_conectades"
        echo ""
        echo "3. Acesse: https://github.com/Bigu-Comunicativismo/conectades-back/settings/secrets/actions"
        echo ""
        echo "4. Leia o arquivo CONFIGURAR_SECRETS_GITHUB.md para instruções detalhadas"
        echo ""
    else
        echo ""
        echo "⚠️  Conexão SSH funcionou, mas algo pode estar errado."
        echo "Verifique manualmente com: ssh -i ~/.ssh/id_rsa_conectades $SSH_USER@$SERVER_IP"
    fi
else
    echo ""
    echo "❌ Erro ao copiar a chave!"
    echo ""
    echo "Tente manualmente:"
    echo "1. Copie a chave pública:"
    echo "   cat ~/.ssh/id_rsa_conectades.pub"
    echo ""
    echo "2. Acesse o servidor:"
    echo "   ssh -p $SSH_PORT $SSH_USER@$SERVER_IP"
    echo ""
    echo "3. No servidor, execute:"
    echo "   mkdir -p ~/.ssh"
    echo "   chmod 700 ~/.ssh"
    echo "   echo 'COLE_A_CHAVE_AQUI' >> ~/.ssh/authorized_keys"
    echo "   chmod 600 ~/.ssh/authorized_keys"
fi

