# RMKit

Sistema em Python para geração automática de documentos jurídicos, desenvolvido para agilizar a rotina de um escritório de advocacia.

## 💡 O problema

A geração de documentos jurídicos (procurações, contratos, entre outros) costumava ser feita manualmente: abrir o Word, localizar e substituir cada campo (nome do cliente, número do processo, endereço, etc.) um por um. Um processo repetitivo, lento e sujeito a erros de digitação.

## ⚙️ Como funciona

O RMKit usa arquivos `.docx` como **templates**, com placeholders no lugar dos dados que variam (ex: `{{nome_cliente}}`, `{{numero_processo}}`, `{{data}}`). O usuário preenche esses dados em uma interface gráfica simples, e o sistema:

1. Lê o template `.docx`
2. Substitui automaticamente todos os placeholders pelas informações inseridas
3. Gera o documento final, pronto para uso

O que antes levava minutos por documento, feito manualmente, passou a levar segundos.

## 🚀 Funcionalidades

- Preenchimento automático de placeholders em documentos `.docx`
- Geração de múltiplos documentos a partir de um único conjunto de dados (kit de documentos)
- Interface gráfica moderna e simples de usar (CustomTkinter)

## 🛠️ Tecnologias

- **Python**
- **CustomTkinter** — interface gráfica
- **python-docx** — leitura e edição de arquivos Word
- **docx2pdf** — conversão para PDF

## ▶️ Como rodar

```bash
git clone https://github.com/GabrielZipp/RMKit.git
cd RMKit
pip install -r requirements.txt
python interface.py
```

> Os templates `.docx` de exemplo neste repositório usam dados fictícios apenas para fins de demonstração.

## 📌 Contexto

Este projeto nasceu de uma necessidade real observada no dia a dia de um escritório de advocacia, onde a geração manual de documentos consumia tempo que poderia ser direcionado a outras atividades. Hoje é usado internamente para agilizar esse processo.

---

Desenvolvido por [Gabriel Juliari](https://github.com/GabrielZipp)
