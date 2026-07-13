# ============================================
# RMKIT - UTILIDADES (utils.py)
# ============================================

import os
import sys
import re
import requests

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def obter_caminho_base():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def formatar_rg(texto):
    alnum = re.sub(r'[^a-zA-Z0-9]', '', texto)
    if len(alnum) > 9:
        alnum = alnum[:9]
    if len(alnum) <= 2:
        return alnum
    elif len(alnum) <= 5:
        return f"{alnum[:2]}.{alnum[2:]}"
    elif len(alnum) <= 8:
        return f"{alnum[:2]}.{alnum[2:5]}.{alnum[5:]}"
    else:
        return f"{alnum[:2]}.{alnum[2:5]}.{alnum[5:8]}-{alnum[8:]}"

def formatar_cpf(texto):
    numeros = re.sub(r'\D', '', texto)
    if len(numeros) > 11:
        numeros = numeros[:11]
    if len(numeros) <= 3:
        return numeros
    elif len(numeros) <= 6:
        return f"{numeros[:3]}.{numeros[3:]}"
    elif len(numeros) <= 9:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:]}"
    else:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"

def consultar_cep(cep):
    cep = re.sub(r'\D', '', cep)
    if len(cep) != 8:
        return None
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        data = response.json()
        if "erro" in data:
            return None
        return {
            "rua": data.get("logradouro", ""),
            "bairro": data.get("bairro", ""),
            "cidade": data.get("localidade", ""),
            "uf": data.get("uf", "")
        }
    except Exception:
        return None