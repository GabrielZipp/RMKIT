# ============================================
# RMKIT - ARQUIVO PRINCIPAL (main.py)
# ============================================

import os
import sys

# Garantir que estamos no diretório certo
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Verificar dependências
try:
    import docx
    import comtypes
    import pythoncom          # vem do pywin32, faltava checar
    import PyPDF2
    import requests
    import customtkinter
    from PIL import Image
except ImportError as e:
    print(f"❌ Erro: Biblioteca não instalada - {e}")
    print("\nExecute: pip install python-docx comtypes pywin32 PyPDF2 requests customtkinter Pillow")
    input("\nPressione Enter para sair...")
    sys.exit(1)

# Iniciar a interface
import interface
interface.app.mainloop()