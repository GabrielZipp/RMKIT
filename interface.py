# ============================================
# RMKIT - INTERFACE GRÁFICA (interface.py)
# VERSÃO FINAL
# ============================================

import customtkinter as ctk
from PIL import Image
from gerador import GeradorKit
import threading
import os
from tkinter import filedialog, messagebox
from utils import resource_path, obter_caminho_base, formatar_rg, formatar_cpf, consultar_cep

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("RMKit - Gerador de Documentos Jurídicos")
app.geometry("600x850")
app.minsize(540, 720)

container = ctk.CTkFrame(app, corner_radius=15)
container.pack(pady=15, padx=15, fill="both", expand=True)

scroll = ctk.CTkScrollableFrame(container, scrollbar_fg_color="transparent")
scroll.pack(fill="both", expand=True, padx=10, pady=10)

try:
    logo_img = ctk.CTkImage(Image.open(resource_path("RMKIT.png")), size=(280, 130))
    ctk.CTkLabel(scroll, image=logo_img, text="").pack(pady=(20, 5))
except:
    ctk.CTkLabel(scroll, text="RMKit", font=("Segoe UI", 30, "bold")).pack(pady=(30, 10))

ctk.CTkLabel(scroll, text="Gerador de Documentos Jurídicos",
             font=("Segoe UI", 18, "bold")).pack(pady=(0, 25))

def campo_com_label(texto_label, valor_padrao=""):
    frame = ctk.CTkFrame(scroll, fg_color="transparent")
    frame.pack(fill="x", pady=8, padx=5)
    ctk.CTkLabel(frame, text=texto_label, anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0,2))
    entry = ctk.CTkEntry(frame, height=38, corner_radius=8, fg_color="#2b2b2b", border_color="#3b3b3b")
    entry.pack(fill="x")
    if valor_padrao:
        entry.insert(0, valor_padrao)
    return entry

entries = {}

entries["nome"] = campo_com_label("Nome Completo")
entries["nacionalidade"] = campo_com_label("Nacionalidade", "brasileiro(a)")
entries["estado_civil"] = campo_com_label("Estado Civil")
entries["profissao"] = campo_com_label("Profissão")

frame_rg = ctk.CTkFrame(scroll, fg_color="transparent")
frame_rg.pack(fill="x", pady=8, padx=5)
ctk.CTkLabel(frame_rg, text="RG", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0,2))
rg_entry = ctk.CTkEntry(frame_rg, height=38, corner_radius=8, fg_color="#2b2b2b", border_color="#3b3b3b")
rg_entry.pack(fill="x")
entries["rg"] = rg_entry

tem_rg = ctk.BooleanVar(value=True)
def toggle_rg():
    if tem_rg.get():
        rg_entry.configure(state="normal", fg_color="#2b2b2b")
    else:
        rg_entry.delete(0, 'end')
        rg_entry.configure(state="disabled", fg_color="#555555")
cb_rg = ctk.CTkCheckBox(frame_rg, text="Possui RG?", variable=tem_rg, command=toggle_rg)
cb_rg.pack(anchor="w", padx=3, pady=(5,0))

frame_cpf = ctk.CTkFrame(scroll, fg_color="transparent")
frame_cpf.pack(fill="x", pady=8, padx=5)
ctk.CTkLabel(frame_cpf, text="CPF", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0,2))
cpf_entry = ctk.CTkEntry(frame_cpf, height=38, corner_radius=8, fg_color="#2b2b2b", border_color="#3b3b3b")
cpf_entry.pack(fill="x")
entries["cpf"] = cpf_entry

frame_cep = ctk.CTkFrame(scroll, fg_color="transparent")
frame_cep.pack(fill="x", pady=8, padx=5)
ctk.CTkLabel(frame_cep, text="CEP", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0,2))
cep_frame = ctk.CTkFrame(frame_cep, fg_color="transparent")
cep_frame.pack(fill="x")
cep_entry = ctk.CTkEntry(cep_frame, height=38, corner_radius=8, fg_color="#2b2b2b", border_color="#3b3b3b")
cep_entry.pack(side="left", fill="x", expand=True)
buscar_cep_btn = ctk.CTkButton(cep_frame, text="Buscar", width=80, height=38, corner_radius=8,
                                fg_color="#1f6eaa", hover_color="#144870", command=lambda: buscar_cep())
buscar_cep_btn.pack(side="right", padx=(5,0))
entries["cep"] = cep_entry

entries["rua"] = campo_com_label("Rua")
entries["numero"] = campo_com_label("Número")
entries["bairro"] = campo_com_label("Bairro")
entries["cidade"] = campo_com_label("Cidade")
entries["estado"] = campo_com_label("Estado (UF)")

def criar_campo_com_botoes(label, botoes_config):
    frame = ctk.CTkFrame(scroll, fg_color="transparent")
    frame.pack(fill="x", pady=8, padx=5)
    ctk.CTkLabel(frame, text=label, anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=3, pady=(0,2))
    linha = ctk.CTkFrame(frame, fg_color="transparent")
    linha.pack(fill="x")
    entry = ctk.CTkEntry(linha, height=38, corner_radius=8, fg_color="#2b2b2b", border_color="#3b3b3b")
    entry.pack(side="left", fill="x", expand=True)
    for texto_botao, valor in botoes_config:
        btn = ctk.CTkButton(linha, text=texto_botao, width=50, height=38, corner_radius=8,
                            fg_color="#3b3b3b", hover_color="#505050",
                            command=lambda v=valor, e=entry: e.delete(0, 'end') or e.insert(0, v))
        btn.pack(side="right", padx=(2,0))
    return entry

entries["tipo_acao"] = criar_campo_com_botoes("Tipo de Ação", [
    ("previdenciária (INSS)", "previdenciária (INSS)"),
    ("trabalhista", "trabalhista"),
    ("inventário", "inventário")
])

entries["honorarios_fixos"] = criar_campo_com_botoes("Honorários Fixos", [("03 sal", "3 (três) salários do benefício obtido"), ("R$ 5k", "R$ 5.000,00")])
entries["honorarios_exito"] = criar_campo_com_botoes("Honorários de Êxito", [("30%", "30% (trinta por cento)"), ("20%", "20% (vinte por cento)")])
entries["multa"] = criar_campo_com_botoes("Multa (cláusula 8)", [("01 sal", "01 (um) salário mínimo"), ("R$ 2k", "R$ 2.000,00")])

frame_opcoes = ctk.CTkFrame(scroll, fg_color="transparent")
frame_opcoes.pack(fill="x", pady=5, padx=5)

tem_honorarios_fixos = ctk.BooleanVar(value=True)
cb_hon_fixos = ctk.CTkCheckBox(frame_opcoes, text="Incluir honorários fixos", variable=tem_honorarios_fixos)
cb_hon_fixos.pack(anchor="w", padx=5, pady=2)

tem_honorarios_exito = ctk.BooleanVar(value=True)
cb_hon_exito = ctk.CTkCheckBox(frame_opcoes, text="Incluir honorários de êxito", variable=tem_honorarios_exito)
cb_hon_exito.pack(anchor="w", padx=5, pady=2)

def buscar_cep():
    dados_cep = consultar_cep(cep_entry.get())
    if not dados_cep:
        messagebox.showerror("Erro", "CEP inválido ou não encontrado.")
        return
    entries["rua"].delete(0, 'end'); entries["rua"].insert(0, dados_cep["rua"])
    entries["bairro"].delete(0, 'end'); entries["bairro"].insert(0, dados_cep["bairro"])
    entries["cidade"].delete(0, 'end'); entries["cidade"].insert(0, dados_cep["cidade"])
    entries["estado"].delete(0, 'end'); entries["estado"].insert(0, dados_cep["uf"])
    status.configure(text="✅ CEP encontrado e campos preenchidos.")

def formatar_rg_event(event=None):
    if tem_rg.get():
        novo = formatar_rg(rg_entry.get())
        if novo != rg_entry.get():
            rg_entry.delete(0, 'end')
            rg_entry.insert(0, novo)

def formatar_cpf_event(event=None):
    novo = formatar_cpf(cpf_entry.get())
    if novo != cpf_entry.get():
        cpf_entry.delete(0, 'end')
        cpf_entry.insert(0, novo)

rg_entry.bind('<KeyRelease>', formatar_rg_event)
cpf_entry.bind('<KeyRelease>', formatar_cpf_event)

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
abrir_btn.grid(row=1, column=0, columnspan=3, pady=(15,0), sticky="ew")

status = ctk.CTkLabel(app, text="✅ Pronto", anchor="w", height=20)
status.pack(side="bottom", fill="x", padx=15, pady=(0,10))

progress = ctk.CTkProgressBar(app, mode="indeterminate", height=4)
progress.pack(side="bottom", fill="x", padx=15, pady=(0,5))
progress.pack_forget()

ultimo_pdf = None

def abrir_pdf():
    if ultimo_pdf and os.path.exists(ultimo_pdf):
        os.startfile(ultimo_pdf)
    else:
        status.configure(text="❌ Nenhum PDF disponível")

gerador = GeradorKit()

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
        '{{HONORARIOS_FIXOS}}': entries["honorarios_fixos"].get().strip() or "03 (três) salários-mínimos",
        '{{HONORARIOS_EXITO}}': entries["honorarios_exito"].get().strip() or "30% (trinta por cento)",
        '{{MULTA_RESICAO}}': entries["multa"].get().strip() or "01 (um) salário-mínimo",
        '{{INCLUIR_HON_FIXOS}}': tem_honorarios_fixos.get(),
        '{{INCLUIR_HON_EXITO}}': tem_honorarios_exito.get(),
    }

def gerar_kit_thread(arquivo, dados):
    try:
        template_proc = resource_path("procuração.docx")
        template_cont = resource_path("contrato.docx")

        if not os.path.exists(template_proc) or not os.path.exists(template_cont):
            app.after(0, lambda: status.configure(text="❌ Templates não encontrados!"))
            return

        gerador.gerar_kit(template_proc, template_cont, dados, arquivo)

        app.after(0, lambda: status.configure(text=f"✅ PDF salvo: {os.path.basename(arquivo)}"))
        app.after(0, lambda: abrir_btn.configure(state="normal", fg_color="#2e7d32", hover_color="#1e5622"))
        app.after(0, lambda: progress.pack_forget())
        app.after(0, lambda: gerar_btn.configure(state="normal"))
        global ultimo_pdf
        ultimo_pdf = arquivo
    except Exception as e:
        app.after(0, lambda: status.configure(text=f"❌ Erro: {str(e)[:100]}..."))
        app.after(0, lambda: progress.pack_forget())
        app.after(0, lambda: gerar_btn.configure(state="normal"))

def iniciar_geracao():
    dados = coletar_dados()
    if not dados['{{NOME}}'] or not dados['{{CPF}}']:
        status.configure(text="❌ Preencha Nome e CPF!")
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
    progress.pack(side="bottom", fill="x", padx=15, pady=(0,5))
    progress.start()

    threading.Thread(target=gerar_kit_thread, args=(arquivo, dados), daemon=True).start()

def limpar_campos():
    for entry in entries.values():
        entry.delete(0, 'end')
    entries["nacionalidade"].insert(0, "brasileiro(a)")
    if not tem_rg.get():
        tem_rg.set(True)
        toggle_rg()
    tem_honorarios_fixos.set(True)
    tem_honorarios_exito.set(True)
    status.configure(text="✅ Campos limpos")
    abrir_btn.configure(state="disabled", fg_color="#2b5e2b")

gerar_btn.configure(command=iniciar_geracao)
limpar_btn.configure(command=limpar_campos)
sair_btn.configure(command=app.quit)

if __name__ == "__main__":
    app.mainloop()