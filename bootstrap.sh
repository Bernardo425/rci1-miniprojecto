#!/bin/bash

# Atualizar os pacotes do sistema
echo "Atualizando os pacotes do sistema..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Instalar Python 3 e pip
echo "Instalando Python 3 e pip..."
sudo apt-get install -y python3 python3-pip

# Configurar o Python 3 como padrão (opcional)
echo "Configurando Python 3 como padrão..."
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Instalar dependências gerais
echo "Instalando dependências gerais..."
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev

# Dependências adicionais (adicione as que você precisar)
echo "Instalando outras dependências úteis..."
sudo apt-get install -y git curl wget

# Configuração de ambiente virtual (opcional)
echo "Instalando virtualenv..."
sudo pip3 install virtualenv

# Limpeza dos pacotes não utilizados
echo "Limpando pacotes desnecessários..."
sudo apt-get autoremove -y
sudo apt-get clean

# Verificar versões instaladas (opcional)
echo "Versões instaladas:"
python --version
pip3 --version
