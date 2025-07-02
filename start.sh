#!/bin/bash

# Instalar dependências Python
echo "Instalando dependências..."
pip install -r requirements.txt

# Iniciar a aplicação Flask
echo "Iniciando aplicação Flask..."
python app.py