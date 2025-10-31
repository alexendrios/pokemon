import requests
import csv
import pandas as pd
from time import sleep
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# URLs da API
BASE_URL = os.getenv("BASE_URL")
LOGIN_URL = f"{BASE_URL}/login"
HEALTH_URL = f"{BASE_URL}/health"
POKEMON_URL = f"{BASE_URL}/pokemon"
COMBATE_URL = f"{BASE_URL}/combats"


# ------------------ Funções de Auxílio ------------------ #


def get_headers(token: str):
    """
    Cria o cabeçalho HTTP com token de autenticação Bearer.

    Args:
        token (str): Token JWT obtido no login.

    Returns:
        dict: Cabeçalho HTTP.
    """
    return {"Authorization": f"Bearer {token}"}


# ------------------ Autenticação ------------------ #


def obter_token_jwt():
    """
    Realiza login na API e retorna a resposta com o token JWT.

    Retorna:
        requests.Response ou None: Objeto Response se login for bem-sucedido, None caso contrário.
    """
    credentials = {"username": "kaizen-poke", "password": "4w9f@D39fkkO"}

    try:
        response = requests.post(LOGIN_URL, json=credentials, timeout=10)
        if response.status_code == 200:
            print(f"✅ Login realizado com sucesso! Token obtido.")
            return response
        else:
            print(f"❌ Falha no login: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print("❌ Erro ao tentar logar:", str(e))
        return None


# ------------------ Verificação da API ------------------ #


def verificar_saude(token):
    """
    Verifica a saúde da API usando token JWT.

    Args:
        token (str): Token JWT para autenticação.
    """
    headers = get_headers(token)

    try:
        response = requests.get(HEALTH_URL, headers=headers)
        if response.status_code == 200:
            print("✅ Acesso autorizado!\nSaúde da Aplicação:")
            print(response.json())
        else:
            print("❌ Erro ao acessar recurso:", response.status_code)
            print(response.text)
    except requests.exceptions.RequestException as e:
        print("❌ Ocorreu um erro na requisição:", str(e))


# ------------------ Coleta de Dados ------------------ #


def obter_dados_pokemon(token):
    """
    Coleta informações básicas de todos os Pokémons da API (paginado).

    Args:
        token (str): Token JWT para autenticação.

    Returns:
        list[tuple]: Lista de tuplas (ID, Nome) dos Pokémons.
    """
    lista_pokemon = []
    headers = get_headers(token)

    print("🔍 Iniciando coleta de dados dos Pokémons...\n")
    try:
        for i in range(1, 51):
            response = requests.get(
                f"{POKEMON_URL}?page={i}&per_page=50", headers=headers
            )

            if response.status_code != 200:
                print(f"❌ Erro na página {i}: {response.status_code}")
                print(response.text)
                break

            dados = response.json()
            pokemons = dados.get("pokemons", [])

            if not pokemons:
                print("✅ Todos os Pokémons foram obtidos.")
                break

            for p in pokemons:
                id_ = p.get("id")
                nome = (p.get("name") or "").strip()
                lista_pokemon.append((id_, nome))

            sleep(1)

    except requests.exceptions.RequestException as e:
        print("❌ Ocorreu um erro na requisição:", str(e))

    print(f"✅ Total de Pokémons coletados: {len(lista_pokemon)}\n")
    return lista_pokemon


def obter_atributos_pokemon(token):
    """
    Coleta atributos detalhados de cada Pokémon com base no CSV de IDs.

    Args:
        token (str): Token JWT para autenticação.

    Returns:
        list[dict]: Lista de dicionários com atributos de cada Pokémon.
    """
    lista_atributos_pokemon = []
    headers = get_headers(token)
    print("🔍 Iniciando coleta dos atributos dos Pokémons...\n")

    try:
        df_id = pd.read_csv("out/pokemons.csv")
        print(f"📂 {len(df_id)} Pokémons carregados do arquivo CSV.\n")

        for pokemon_id in df_id["ID"]:
            response = requests.get(f"{POKEMON_URL}/{pokemon_id}", headers=headers)

            if response.status_code != 200:
                print(
                    f"❌ Erro ao consultar os atributos do Pokémon {pokemon_id}: {response.status_code}"
                )
                print(response.text)
                continue

            dados = response.json()

            lista_atributos_pokemon.append(
                {
                    "ID": dados.get("id"),
                    "Nome": dados.get("name").strip(),
                    "Hp": dados.get("hp"),
                    "Attack": dados.get("attack"),
                    "Defense": dados.get("defense"),
                    "Sp_attack": dados.get("sp_attack"),
                    "Sp_defense": dados.get("sp_defense"),
                    "Speed": dados.get("speed"),
                    "Generation": dados.get("generation"),
                    "Legendary": dados.get("legendary"),
                    "Types": dados.get("types", []),
                }
            )

            sleep(0.5)

        print(
            f"\n✅ Total de atributos dos Pokémons detalhados: {len(lista_atributos_pokemon)}"
        )

    except FileNotFoundError:
        print("❌ Arquivo 'pokemons.csv' não encontrado.")
    except requests.exceptions.RequestException as e:
        print("❌ Erro de conexão com a API:", str(e))
    except Exception as e:
        print("⚠️ Erro inesperado:", str(e))

    return lista_atributos_pokemon


def obter_dados_combate(token):
    """
    Coleta dados de combates entre Pokémons (paginado).

    Args:
        token (str): Token JWT para autenticação.

    Returns:
        list[dict]: Lista de combates com ID do primeiro Pokémon, segundo Pokémon e vencedor.
    """
    lista_combates = []
    headers = get_headers(token)

    print("🔍 Iniciando coleta de dados de combates...\n")
    try:
        for i in range(1, 501):
            response = requests.get(
                f"{COMBATE_URL}?page={i}&per_page=100", headers=headers
            )

            if response.status_code != 200:
                print(f"❌ Erro na página {i}: {response.status_code}")
                print(response.text)
                break

            dados = response.json()
            combates = dados.get("combats", [])

            if not combates:
                print("✅ Todos os dados dos combates foram obtidos.")
                break

            for c in combates:
                lista_combates.append(
                    {
                        "first_pokemon": c.get("first_pokemon"),
                        "second_pokemon": c.get("second_pokemon"),
                        "winner": c.get("winner"),
                    }
                )

    except requests.exceptions.RequestException as e:
        print("❌ Ocorreu um erro na requisição:", str(e))

    print(f"✅ Total de combates realizados: {len(lista_combates)}\n")
    return lista_combates


# ------------------ Transformação para CSV ------------------ #


def transformar_csv(dados, file_):
    """
    Salva os dados coletados em arquivos CSV no diretório 'out'.

    Args:
        dados (list/tuple): Dados a serem salvos.
        file_ (str): Tipo de dado ('pokemons', 'atributos_pokemon', 'combates').

    Cria:
        CSV no formato apropriado para cada tipo de dado.
    """
    if file_ == "pokemons":
        with open(f"out/{file_}.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Nome"])
            for id_, nome in dados:
                writer.writerow([id_, nome])
    elif file_ == "atributos_pokemon":
        with open(f"out/{file_}.csv", mode="w", newline="", encoding="utf-8") as file:
            fieldnames = [
                "ID",
                "Nome",
                "Hp",
                "Attack",
                "Defense",
                "Sp_attack",
                "Sp_defense",
                "Speed",
                "Generation",
                "Legendary",
                "Types",
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for item in dados:
                writer.writerow(item)
    elif file_ == "combates":
        with open(f"out/{file_}.csv", mode="w", newline="", encoding="utf-8") as file:
            fieldnames = ["first_pokemon", "second_pokemon", "winner"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for item in dados:
                writer.writerow(item)

    print(f"💾 Dados salvos em '{file_}.csv' com sucesso!")
