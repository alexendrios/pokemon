# -------------------------------
# Imagem base
# -------------------------------
FROM python:3.13.0

# Diretório de trabalho
WORKDIR /app

# Copiar dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar toda a aplicação
COPY . .

# Variáveis de ambiente base
ENV PYTHONUNBUFFERED=1

# Expor a porta do Streamlit
EXPOSE 8501

# Comando padrão: executar pipeline e depois dashboard
CMD ["bash", "-c", "python -m src.run_pipeline && python -m streamlit run dashboard/dashboard.py --server.port 8501 --server.address 0.0.0.0"]
