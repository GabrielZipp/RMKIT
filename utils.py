# ============================================
# RMKIT - UTILIDADES (utils.py)
# VERSÃO FINAL
# ============================================

import os
import sys
import re
import requests


def resource_path(relative_path):
    """Caminho absoluto para recursos (funciona com PyInstaller)."""
    try:
        base_path = sys._MEIPASS
    except Exception:
<<<<<<< HEAD
        # Corrigido: usa o diretório do script, não o CWD
=======
        # Usa o diretório do script, não o CWD
>>>>>>> 5b56f14 (correção de bug na abertura de pdf)
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def obter_caminho_base():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
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


def cpf_valido(cpf):
    """Valida CPF pelo algoritmo dos dígitos verificadores."""
    nums = re.sub(r'\D', '', cpf or '')
    if len(nums) != 11 or nums == nums[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(nums[j]) * ((i + 1) - j) for j in range(i))
        dig = (soma * 10 % 11) % 10
        if dig != int(nums[i]):
            return False
    return True


def consultar_cep(cep):
    cep = re.sub(r'\D', '', cep or '')
    if len(cep) != 8:
        return None
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        response.raise_for_status()
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


# ---------- Números por extenso (para os botões incrementais) ----------

_UNIDADES = ['zero', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove',
             'dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis',
             'dezessete', 'dezoito', 'dezenove']
_DEZENAS = ['', '', 'vinte', 'trinta', 'quarenta', 'cinquenta',
            'sessenta', 'setenta', 'oitenta', 'noventa']
_CENTENAS = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos',
             'seiscentos', 'setecentos', 'oitocentos', 'novecentos']


def numero_por_extenso(n):
    """Suporta 0-999 (suficiente para honorários e percentuais)."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return str(n)
    if n < 0 or n > 999:
        return str(n)
    if n < 20:
        return _UNIDADES[n]
    if n < 100:
        d, u = divmod(n, 10)
        return _DEZENAS[d] if u == 0 else f"{_DEZENAS[d]} e {_UNIDADES[u]}"
    c, r = divmod(n, 100)
    if r == 0:
        return 'cem' if c == 1 else _CENTENAS[c]
    return f"{_CENTENAS[c]} e {numero_por_extenso(r)}"