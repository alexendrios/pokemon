# ⚡ Pokémon Analytics — Powered by FPRA | TP | ARKSOW

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive-ff4b4b?logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Data--Layer-336791?logo=postgresql)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

> **Pokémon Analytics** é um ecossistema de **engenharia de dados, análise estatística e visualização interativa**, desenvolvido sob os princípios da engenharia **FPRA | TP | ARKSOW**.  
> O projeto representa **inovação aplicada**, **excelência técnica** e **integração entre dados e inteligência visual**, consolidando uma arquitetura de nível profissional e reprodutível.

---

## 🧠 Visão Estratégica

A solução entrega uma **pipeline completa de dados**, cobrindo todas as camadas — da ingestão à apresentação — integrando:

- 🔹 **Engenharia de Dados:** ETL automatizado com *Pandas* + *SQLAlchemy*  
- 🔹 **Análise Estatística:** limpeza, validação e modelagem inteligente de dados  
- 🔹 **Visualização Interativa:** *dashboard* Streamlit com insights dinâmicos e comparativos  
- 🔹 **Relatórios Profissionais:** geração automática de PDFs com identidade visual FPRA | TP | ARKSOW  
- 🔹 **Infraestrutura Contêinerizada:** execução orquestrada com *Docker Compose* para máxima portabilidade  

---

## 🏗️ Arquitetura Profissional

### ⚙️ Componentes Técnicos

| **Camada**                     | **Descrição**                                     | **Tecnologias**                                  |
| ------------------------------ | ------------------------------------------------- | ------------------------------------------------ |
| 🛰️ **Ingestão de Dados**       | Coleta autenticada via API (JWT)                  | `requests`, `dotenv`                             |
| 🔄 **Transformação (ETL)**     | Limpeza, normalização e persistência dos dados    | `pandas`, `sqlalchemy`, `psycopg2`               |
| 🐘 **Armazenamento**           | Banco relacional local ou em nuvem (Supabase)     | `PostgreSQL`, `Docker`                           |
| 📊 **Análise e Relatórios**    | Estatísticas, visualizações e relatórios PDF      | `matplotlib`, `seaborn`, `plotly`, `streamlit`   |
| ⚙️ **Orquestração**            | Execução automatizada e reprodutível              | `docker-compose`, `Makefile` *(opcional)*        |

---

## ⚡ Funcionalidades Principais

### 🔹 Pipeline Automatizado

- Coleta e autenticação de dados via **JWT**  
- Transformação e persistência de **atributos e combates Pokémon**  
- Armazenamento seguro em **PostgreSQL**  
- **Relatórios PDF** com metadados e visualizações avançadas  

### 🔹 Dashboard Interativo

- **Top 10 Pokémon** (vitórias e derrotas)  
- Gráficos dinâmicos: **barras**, **radar** e **comparativos**  
- Análises de desempenho com **média global**  
- Exportação em **HTML estilizado**  

### 🔹 Relatórios Profissionais

- PDFs automáticos com identidade **FPRA | TP | ARKSOW**  
- **Sumário técnico** e visualizações integradas  
- **Controle de versão** e automação contínua  

---

## 🧩 Estrutura do Projeto

```bash
.

├── src/ # Núcleo da pipeline (ETL e integração)
│ ├── obtencao_dados.py # Coleta e autenticação via API
│ ├── tratamento_dados.py # Limpeza e transformação
│ ├── analisar_dados_banco.py # Análise estatística no DB
│ ├── report_analise.py # Geração de relatórios PDF
│ └── run_pipeline.py # Execução completa do pipeline
│
├── dashboard/ # Dashboard Streamlit
│ └── dashboard.py
|__ dcos/ # MANIFESTO_FPRA_TP_ARKSOW
├── report/ # Relatórios automáticos
├── out/ # Dados brutos e transformados
├── Dockerfile # Build da aplicação
├── docker-compose.yml # Orquestração dos serviços
├── requirements.txt # Dependências do projeto
└── README.md # Documentação oficial

```

---

## 🔐 Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto com as seguintes chaves (exemplo seguro):

```bash
POSTGRES_USERNAME=<seu_usuario>
POSTGRES_PASSWORD=<sua_senha>
POSTGRES_DB=<seu_banco>
POSTGRES_HOST=<seu_host>
POSTGRES_PORT=5432
REQUISITOS_SSL=?sslmode=require
BASE_URL=<url_da_api>

```

---
## 🧩 Pré-requisitos Antes de iniciar, certifique-se de ter instalado:
 - 🐳 **Docker** e **Docker Compose**
 - 🐍 **Python 3.11+** 
 - 🌿 **Git** (para versionamento e colaboração)

---

## 🚀 Execução ### Via Docker (recomendado)
```bash
# Build da imagem
docker-compose up --build

```

---

### Execução Manual (sem Docker)

1. **Clonar o repositório:**

```bash
git clone https://github.com/alexendrios/pokemon.git
cd pokemon

```

---

2. **Criar e ativar um ambiente virtual:**

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

```

---

3. **Instalar as dependências:**

```bash
pip install -r requirements.txt

```

---

### 🔧 Configuração de Variáveis de Ambiente 1. Na raiz do projeto, crie um arquivo chamado .env.

2. Adicione suas credenciais e URLs de API seguindo o modelo:

POSTGRES_USERNAME=<seu_usuario>
POSTGRES_PASSWORD=<sua_senha>
POSTGRES_HOST=<seu_host>
POSTGRES_PORT=5432
POSTGRES_DB=<seu_banco>
REQUISITOS_SSL=?sslmode=require
BASE_URL=<url_da_api>

---

1. **Executar o pipeline:**

```bash
python src/run_pipeline.py 6. 

```

---

**Iniciar o dashboard**
```bash
streamlit run dashboard/dashboard.py

```

---

🔖 Consulte também o [MANIFESTO FPRA | TP | ARKSOW](./docs/MANIFESTO_FPRA_TP_ARKSOW.md)

---
> 👨‍💻 Autor **Alexandre Pereira Santos** 
>
> 🏆 Senior Software Engineer in Quality (QA) — Brasília/DF 
>
> 🧬 Expertise: Arquitetura de Software • Engenharia de Qualidade • Big Data • Machine Learning 
>
> 🔗 [LinkedIn](https://www.linkedin.com/in/alexendrios/)
