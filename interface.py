# ============================================
# RMKIT - INTERFACE GRÁFICA (interface.py)
<<<<<<< HEAD
# VERSÃO FINAL COM MELHORIAS
=======
# VERSÃO FINAL COM MELHORIAS + FIX DO BOTÃO ABRIR PDF
>>>>>>> 5b56f14 (correção de bug na abertura de pdf)
# ============================================

import customtkinter as ctk
from PIL import Image
from gerador import GeradorKit
import threading
import os
import re
from tkinter import filedialog, messagebox
from utils import (
    resource_path, formatar_rg, formatar_cpf, consultar_cep,
    cpf_valido, numero_por_extenso
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("RMKit - Gerador de Documentos Jurídicos")
app.geometry("620x900")
app.minsize(560, 740)

# Fechar corretamente liberando recursos
app.protocol("WM_DELETE_WINDOW", lambda: app.destroy())

container = ctk.CTkFrame(app, corner_radius=15)
container.pack(pady=15, padx=15, fill="both", expand=True)

# ---------- Rodapé fixo (fora do scroll) ----------
footer = ctk.CTkFrame(app, fg_color="transparent")
footer.pack(side="bottom", fill="x", padx=15, pady=(0, 10))

status = ctk.CTkLabel(footer, text="✅ Pronto", anchor="w", height=20)
status.pack(fill="x")

progress = ctk.CTkProgressBar(footer, mode="indeterminate", height=4)

# ---------- Área rolável ----------
scroll = ctk.CTkScrollableFrame(container, scrollbar_fg_color="transparent")
scroll.pack(fill="both", expand=True, padx=10, pady=10)

try:
    logo_img = ctk.CTkImage(Image.open(resource_path("RMKIT.png")), size=(280, 130))
    ctk.CTkLabel(scroll, image=logo_img, text="").pack(pady=(20, 5))
except Exception:
    ctk.CTkLabel(scroll, text="RMKit", font=("Segoe UI", 30, "bold")).pack(pady=(30, 10))

ctk.CTkLabel(scroll, text="Gerador de Documentos Jurídicos",
             font=("Segoe UI", 18, "bold")).pack(pady=(0, 25))

entries = {}

# ---------- Fábricas de campo ----------

def campo_com_label(texto_label, valor_padrao=""):
    frame = ctk.CTkFrame(scroll, fg_color="transparent")
    frame.pack(fill="x", pady=8, padx=5)
    ctk.CTkLabel(frame, text=texto_label, anchor="w",
                 font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0, 2))
    entry = ctk.CTkEntry(frame, height=38, corner_radius=8,
                         fg_color="#2b2b2b", border_color="#3b3b3b")
    entry.pack(fill="x")
    if valor_padrao:
        entry.insert(0, valor_padrao)
    return entry


def campo_combo(texto_label, opcoes, valor_padrao=""):
    frame = ctk.CTkFrame(scroll, fg_color="transparent")
    frame.pack(fill="x", pady=8, padx=5)
    ctk.CTkLabel(frame, text=texto_label, anchor="w",
                 font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0, 2))
    combo = ctk.CTkComboBox(
        frame, values=opcoes, height=38, corner_radius=8,
        fg_color="#2b2b2b", border_color="#3b3b3b",
        button_color="#3b3b3b", button_hover_color="#505050",
        dropdown_fg_color="#2b2b2b", dropdown_hover_color="#1f6eaa",
    )
    combo.set(valor_padrao or "")
    combo.pack(fill="x")
    return combo


def _set_entry(entry, valor):
    entry.delete(0, 'end')
    if valor:
        entry.insert(0, valor)


def criar_campo_com_botoes(label, botoes_config, largura_botao=80, on_click=None):
    """Botões que SETAM um valor fixo no campo (ex.: tipo de ação)."""
    frame = ctk.CTkFrame(scroll, fg_color="transparent")
    frame.pack(fill="x", pady=8, padx=5)
    ctk.CTkLabel(frame, text=label, anchor="w",
                 font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0, 2))
    linha = ctk.CTkFrame(frame, fg_color="transparent")
    linha.pack(fill="x")
    entry = ctk.CTkEntry(linha, height=38, corner_radius=8,
                         fg_color="#2b2b2b", border_color="#3b3b3b")
    entry.pack(side="left", fill="x", expand=True)

    for texto_botao, valor in botoes_config:
        btn = ctk.CTkButton(linha, text=texto_botao,
                            width=largura_botao, height=38, corner_radius=8,
                            fg_color="#3b3b3b", hover_color="#505050")
        btn.pack(side="right", padx=(2, 0))

        def make_handler(e=entry, v=valor, cb=on_click):
            def handler():
                _set_entry(e, v)
                if cb:
                    cb(v)
            return handler

        btn.configure(command=make_handler())
    return entry


def criar_campo_incremento(label, incrementadores):
    """
    Botões que INCREMENTAM o valor atual do campo.
    incrementadores: lista de (texto_botao, formatador, step)
    - formatador(n) -> str
    - step: quanto somar ao número extraído do campo (default 1)
    """
    frame = ctk.CTkFrame(scroll, fg_color="transparent")
    frame.pack(fill="x", pady=8, padx=5)
    ctk.CTkLabel(frame, text=label, anchor="w",
                 font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0, 2))
    linha = ctk.CTkFrame(frame, fg_color="transparent")
    linha.pack(fill="x")
    entry = ctk.CTkEntry(linha, height=38, corner_radius=8,
                         fg_color="#2b2b2b", border_color="#3b3b3b")
    entry.pack(side="left", fill="x", expand=True)

    for texto_botao, formatar, step in incrementadores:
        btn = ctk.CTkButton(linha, text=texto_botao,
                            width=80, height=38, corner_radius=8,
                            fg_color="#3b3b3b", hover_color="#505050")
        btn.pack(side="right", padx=(2, 0))

        def make_handler(e=entry, fmt=formatar, st=step):
            def handler():
                texto = e.get().strip()
                m = re.search(r'\d+', texto)
                n = (int(m.group(0)) + st) if m else st
                _set_entry(e, fmt(n))
            return handler

        btn.configure(command=make_handler())
    return entry


# ---------- Campos básicos ----------

entries["nome"] = campo_com_label("Nome Completo")
entries["nacionalidade"] = campo_com_label("Nacionalidade", "brasileiro(a)")

<<<<<<< HEAD
# Estado civil: agora é combo
=======
# Estado civil: combo
>>>>>>> 5b56f14 (correção de bug na abertura de pdf)
entries["estado_civil"] = campo_combo(
    "Estado Civil",
    ["solteiro(a)", "casado(a)", "viúvo(a)", "divorciado(a)"]
)

entries["profissao"] = campo_com_label("Profissão")

# ---------- RG ----------
frame_rg = ctk.CTkFrame(scroll, fg_color="transparent")
frame_rg.pack(fill="x", pady=8, padx=5)
ctk.CTkLabel(frame_rg, text="RG", anchor="w",
             font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0, 2))
rg_entry = ctk.CTkEntry(frame_rg, height=38, corner_radius=8,
                        fg_color="#2b2b2b", border_color="#3b3b3b")
rg_entry.pack(fill="x")
entries["rg"] = rg_entry

tem_rg = ctk.BooleanVar(value=True)


def toggle_rg():
    if tem_rg.get():
        rg_entry.configure(state="normal", fg_color="#2b2b2b")
    else:
        rg_entry.delete(0, 'end')
        rg_entry.configure(state="disabled", fg_color="#555555")


ctk.CTkCheckBox(frame_rg, text="Possui RG?", variable=tem_rg,
                command=toggle_rg).pack(anchor="w", padx=3, pady=(5, 0))

# ---------- CPF ----------
frame_cpf = ctk.CTkFrame(scroll, fg_color="transparent")
frame_cpf.pack(fill="x", pady=8, padx=5)
ctk.CTkLabel(frame_cpf, text="CPF", anchor="w",
             font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0, 2))
cpf_entry = ctk.CTkEntry(frame_cpf, height=38, corner_radius=8,
                         fg_color="#2b2b2b", border_color="#3b3b3b")
cpf_entry.pack(fill="x")
entries["cpf"] = cpf_entry

# ---------- CEP + endereço ----------
frame_cep = ctk.CTkFrame(scroll, fg_color="transparent")
frame_cep.pack(fill="x", pady=8, padx=5)
ctk.CTkLabel(frame_cep, text="CEP", anchor="w",
             font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0, 2))
cep_frame = ctk.CTkFrame(frame_cep, fg_color="transparent")
cep_frame.pack(fill="x")
cep_entry = ctk.CTkEntry(cep_frame, height=38, corner_radius=8,
                         fg_color="#2b2b2b", border_color="#3b3b3b")
cep_entry.pack(side="left", fill="x", expand=True)
buscar_cep_btn = ctk.CTkButton(cep_frame, text="Buscar", width=80, height=38,
                               corner_radius=8, fg_color="#1f6eaa",
                               hover_color="#144870",
                               command=lambda: buscar_cep())
buscar_cep_btn.pack(side="right", padx=(5, 0))
entries["cep"] = cep_entry

entries["rua"] = campo_com_label("Rua")
entries["numero"] = campo_com_label("Número")
entries["bairro"] = campo_com_label("Bairro")
entries["cidade"] = campo_com_label("Cidade")
entries["estado"] = campo_com_label("Estado (UF)")


<<<<<<< HEAD
# ---------- Presets por tipo de ação ----------
=======
# ---------- Formatadores de valor ----------
>>>>>>> 5b56f14 (correção de bug na abertura de pdf)

def _fmt_salario(n):
    plural = "s" if n != 1 else ""
    return f"{n:02d} ({numero_por_extenso(n)}) salário{plural} mínimo{plural}"


def _fmt_salario_beneficio(n):
    plural = "s" if n != 1 else ""
    return f"{n:02d} ({numero_por_extenso(n)}) salário{plural} do benefício obtido"


def _fmt_reais(n):
    return f"R$ {n}.000,00"


def _fmt_percentual(n):
    return f"{n}% ({numero_por_extenso(n)} por cento)"


<<<<<<< HEAD
=======
# ---------- Presets por tipo de ação ----------

>>>>>>> 5b56f14 (correção de bug na abertura de pdf)
def aplicar_preset(tipo):
    """Preenche automaticamente honorários conforme tipo de ação."""
    t = tipo.lower()
    if "inss" in t or "previdenci" in t:
        tem_honorarios_fixos.set(True)
        _set_entry(entries["honorarios_fixos"], _fmt_salario_beneficio(3))
        _set_entry(entries["honorarios_exito"], _fmt_percentual(30))
        _set_entry(entries["multa"], _fmt_salario(1))
    elif "trabalhista" in t:
        tem_honorarios_fixos.set(False)
        _set_entry(entries["honorarios_fixos"], "")
        _set_entry(entries["honorarios_exito"], _fmt_percentual(30))
        _set_entry(entries["multa"], _fmt_salario(1))
    elif "invent" in t:
        tem_honorarios_fixos.set(False)
        _set_entry(entries["honorarios_fixos"], "")
        _set_entry(entries["honorarios_exito"], _fmt_percentual(30))
        _set_entry(entries["multa"], _fmt_salario(1))


# ---------- Tipo de ação (com preset) ----------
entries["tipo_acao"] = criar_campo_com_botoes(
    "Tipo de Ação",
    [
        ("INSS", "previdenciária (INSS)"),
        ("Trabalhista", "trabalhista"),
        ("Inventário", "inventário"),
    ],
    largura_botao=85,
    on_click=aplicar_preset,
)

# ---------- Honorários (botões incrementais) ----------
entries["honorarios_fixos"] = criar_campo_incremento(
    "Honorários Fixos",
    [
        ("+ R$1k", _fmt_reais, 1),
        ("+ Sal", _fmt_salario, 1),
    ]
)

entries["honorarios_exito"] = criar_campo_incremento(
    "Honorários de Êxito",
    [
        ("+10%", _fmt_percentual, 10),
        ("+5%", _fmt_percentual, 5),
    ]
)

entries["multa"] = criar_campo_incremento(
    "Multa (cláusula 8)",
    [
        ("+ R$1k", _fmt_reais, 1),
        ("+ Sal", _fmt_salario, 1),
    ]
)

# ---------- Checkboxes de inclusão ----------
frame_opcoes = ctk.CTkFrame(scroll, fg_color="transparent")
frame_opcoes.pack(fill="x", pady=5, padx=5)

tem_honorarios_fixos = ctk.BooleanVar(value=True)
ctk.CTkCheckBox(frame_opcoes, text="Incluir honorários fixos",
                variable=tem_honorarios_fixos).pack(anchor="w", padx=5, pady=2)

tem_honorarios_exito = ctk.BooleanVar(value=True)
ctk.CTkCheckBox(frame_opcoes, text="Incluir honorários de êxito",
                variable=tem_honorarios_exito).pack(anchor="w", padx=5, pady=2)


# ---------- Callbacks ----------

def buscar_cep():
    dados_cep = consultar_cep(cep_entry.get())
    if not dados_cep:
        messagebox.showerror("Erro", "CEP inválido ou não encontrado.")
        return
    _set_entry(entries["rua"], dados_cep["rua"])
    _set_entry(entries["bairro"], dados_cep["bairro"])
    _set_entry(entries["cidade"], dados_cep["cidade"])
    _set_entry(entries["estado"], dados_cep["uf"])
    status.configure(text="✅ CEP encontrado e campos preenchidos.")


def formatar_rg_event(event=None):
    if tem_rg.get() and event and event.keysym not in ("Left", "Right", "Home", "End"):
        novo = formatar_rg(rg_entry.get())
        if novo != rg_entry.get():
            rg_entry.delete(0, 'end')
            rg_entry.insert(0, novo)


def formatar_cpf_event(event=None):
    if event and event.keysym in ("Left", "Right", "Home", "End"):
        return
    novo = formatar_cpf(cpf_entry.get())
    if novo != cpf_entry.get():
        cpf_entry.delete(0, 'end')
        cpf_entry.insert(0, novo)


rg_entry.bind('<KeyRelease>', formatar_rg_event)
cpf_entry.bind('<KeyRelease>', formatar_cpf_event)
# Colar também dispara formatação
rg_entry.bind('<<Paste>>', lambda e: app.after(10, formatar_rg_event))
cpf_entry.bind('<<Paste>>', lambda e: app.after(10, formatar_cpf_event))


# ---------- Botões principais ----------
botoes_frame = ctk.CTkFrame(scroll, fg_color="transparent")
botoes_frame.pack(pady=25)

gerar_btn = ctk.CTkButton(botoes_frame, text="⚡ GERAR KIT", width=130, height=40,
                          corner_radius=12, fg_color="#1f6eaa", hover_color="#144870")
gerar_btn.grid(row=0, column=0, padx=6)

limpar_btn = ctk.CTkButton(botoes_frame, text="🗑️ LIMPAR", width=130, height=40,
                           corner_radius=12, fg_color="#3b3b3b", hover_color="#505050")
limpar_btn.grid(row=0, column=1, padx=6)

sair_btn = ctk.CTkButton(botoes_frame, text="🚪 SAIR", width=130, height=40,
                         corner_radius=12, fg_color="#aa3333", hover_color="#882222")
sair_btn.grid(row=0, column=2, padx=6)

abrir_btn = ctk.CTkButton(botoes_frame, text="📂 ABRIR PDF", width=130, height=40,
                          corner_radius=12, fg_color="#2b5e2b", hover_color="#1e451e",
                          state="disabled", command=lambda: abrir_pdf())
abrir_btn.grid(row=1, column=0, columnspan=3, pady=(15, 0), sticky="ew")

# ---------- Estado ----------
gerador = GeradorKit()
ultimo_pdf = {"path": None}


def abrir_pdf():
<<<<<<< HEAD
    if ultimo_pdf["path"] and os.path.exists(ultimo_pdf["path"]):
        try:
            os.startfile(ultimo_pdf["path"])
        except Exception as e:
            status.configure(text=f"❌ Erro ao abrir: {e}")
    else:
=======
    caminho = ultimo_pdf.get("path")
    if not caminho:
>>>>>>> 5b56f14 (correção de bug na abertura de pdf)
        status.configure(text="❌ Nenhum PDF disponível")
        return
    if not os.path.exists(caminho):
        status.configure(text="❌ Arquivo não encontrado (foi movido ou apagado?)")
        return
    try:
        os.startfile(caminho)
        status.configure(text=f"📂 Abrindo: {os.path.basename(caminho)}")
    except Exception as e:
        status.configure(text=f"❌ Erro ao abrir: {e}")
        messagebox.showerror("Erro ao abrir PDF",
                             f"Não foi possível abrir:\n{caminho}\n\n{e}")


# ---------- Coleta e geração ----------

def coletar_dados():
    rg_valor = entries["rg"].get().strip() if tem_rg.get() else ""
    return {
        '{{NOME}}': entries["nome"].get().strip(),
        '{{NACIONALIDADE}}': entries["nacionalidade"].get().strip(),
        '{{ESTADO_CIVIL}}': entries["estado_civil"].get().strip(),
        '{{PROFISSAO}}': entries["profissao"].get().strip(),
        '{{RG}}': rg_valor,
        '{{CPF}}': entries["cpf"].get().strip(),
        '{{RUA}}': entries["rua"].get().strip(),
        '{{NUMERO}}': entries["numero"].get().strip(),
        '{{BAIRRO}}': entries["bairro"].get().strip(),
        '{{CEP}}': entries["cep"].get().strip(),
        '{{CIDADE}}': entries["cidade"].get().strip(),
        '{{ESTADO}}': entries["estado"].get().strip(),
        '{{TIPO_ACAO}}': entries["tipo_acao"].get().strip(),
        '{{HONORARIOS_FIXOS}}': entries["honorarios_fixos"].get().strip(),
        '{{HONORARIOS_EXITO}}': entries["honorarios_exito"].get().strip(),
        '{{MULTA_RESICAO}}': entries["multa"].get().strip(),
        '{{INCLUIR_HON_FIXOS}}': tem_honorarios_fixos.get(),
        '{{INCLUIR_HON_EXITO}}': tem_honorarios_exito.get(),
    }


<<<<<<< HEAD
def _reset_ui():
    progress.pack_forget()
    gerar_btn.configure(state="normal")
    abrir_btn.configure(state="disabled", fg_color="#2b5e2b")


=======
# ---------- Reset helpers (o fix do bug está aqui) ----------

def _reset_progresso():
    """Só limpa a barra e reabilita o botão Gerar (usar no sucesso)."""
    progress.stop()
    progress.pack_forget()
    gerar_btn.configure(state="normal")


def _reset_completo():
    """Limpa tudo e desabilita o Abrir PDF (usar em erro)."""
    _reset_progresso()
    abrir_btn.configure(state="disabled", fg_color="#2b5e2b")


def _on_sucesso(arquivo):
    """Callback na thread principal após geração bem-sucedida."""
    ultimo_pdf["path"] = arquivo
    status.configure(text=f"✅ PDF salvo: {os.path.basename(arquivo)}")
    abrir_btn.configure(state="normal", fg_color="#2e7d32", hover_color="#1e5622")
    _reset_progresso()


def _on_erro(msg):
    """Callback na thread principal em caso de erro."""
    status.configure(text=f"❌ Erro: {msg}")
    _reset_completo()


>>>>>>> 5b56f14 (correção de bug na abertura de pdf)
def gerar_kit_thread(arquivo, dados):
    try:
        template_proc = resource_path("procuração.docx")
        template_cont = resource_path("contrato.docx")

        if not os.path.exists(template_proc) or not os.path.exists(template_cont):
<<<<<<< HEAD
            app.after(0, lambda: status.configure(text="❌ Templates não encontrados!"))
            app.after(0, _reset_ui)
            return

        gerador.gerar_kit(template_proc, template_cont, dados, arquivo)

        ultimo_pdf["path"] = arquivo
        app.after(0, lambda: status.configure(
            text=f"✅ PDF salvo: {os.path.basename(arquivo)}"))
        app.after(0, lambda: abrir_btn.configure(
            state="normal", fg_color="#2e7d32", hover_color="#1e5622"))
        app.after(0, _reset_ui)
    except Exception as e:
        msg = str(e)[:120]
        app.after(0, lambda: status.configure(text=f"❌ Erro: {msg}"))
        app.after(0, _reset_ui)
=======
            app.after(0, lambda: _on_erro("Templates não encontrados!"))
            return

        gerador.gerar_kit(template_proc, template_cont, dados, arquivo)
        app.after(0, lambda: _on_sucesso(arquivo))
    except Exception as e:
        msg = str(e)[:120]
        app.after(0, lambda m=msg: _on_erro(m))
>>>>>>> 5b56f14 (correção de bug na abertura de pdf)


def iniciar_geracao():
    dados = coletar_dados()

    if not dados['{{NOME}}']:
        status.configure(text="❌ Preencha o Nome!")
        return
    if not dados['{{CPF}}']:
        status.configure(text="❌ Preencha o CPF!")
        return
    if not cpf_valido(dados['{{CPF}}']):
        if not messagebox.askyesno(
            "CPF inválido",
            "O CPF informado não passou na validação dos dígitos.\n\nDeseja continuar mesmo assim?"
        ):
            status.configure(text="❌ Geração cancelada.")
            return

    nome_padrao = f"Kit_{dados['{{NOME}}'].replace(' ', '_')}.pdf"
    arquivo = filedialog.asksaveasfilename(
        title="Salvar kit como",
        defaultextension=".pdf",
        initialfile=nome_padrao,
        filetypes=[("PDF", "*.pdf")]
    )
    if not arquivo:
        status.configure(text="✅ Pronto")
        return

    gerar_btn.configure(state="disabled")
    abrir_btn.configure(state="disabled", fg_color="#2b5e2b")
    status.configure(text="⏳ Gerando...")
    progress.pack(fill="x", pady=(5, 0))
    progress.start()

    threading.Thread(target=gerar_kit_thread,
                     args=(arquivo, dados), daemon=True).start()


def limpar_campos():
    for key, widget in entries.items():
        if isinstance(widget, ctk.CTkComboBox):
            widget.set("")
        else:
            widget.delete(0, 'end')
    entries["nacionalidade"].insert(0, "brasileiro(a)")
    if not tem_rg.get():
        tem_rg.set(True)
        toggle_rg()
    tem_honorarios_fixos.set(True)
    tem_honorarios_exito.set(True)
    status.configure(text="✅ Campos limpos")
    abrir_btn.configure(state="disabled", fg_color="#2b5e2b")
    ultimo_pdf["path"] = None


gerar_btn.configure(command=iniciar_geracao)
limpar_btn.configure(command=limpar_campos)
sair_btn.configure(command=app.destroy)

if __name__ == "__main__":
    app.mainloop()