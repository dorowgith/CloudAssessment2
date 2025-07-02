#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Install dependencies using python3 -m pip
echo "Instalando dependências..."
python3 -m pip install -r requirements.txt

# Start Flask application
echo "Iniciando aplicação Flask..."
python3 app.py