# ============================================
# RMKIT - MÓDULO DE LÓGICA (gerador.py)
# VERSÃO FINAL
# ============================================

import os
import tempfile
import shutil
import threading
from datetime import datetime
import comtypes.client
import PyPDF2
import pythoncom
from docx import Document

class GeradorKit:
    def data_por_extenso(self):
        meses = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        hoje = datetime.now()
        return f"{hoje.day} de {meses[hoje.month]} de {hoje.year}"

    def gerar_frase_rg(self, rg_numero):
        if not rg_numero or not rg_numero.strip():
            return ""
        return f"portador(a) da cédula de identidade RG nº {rg_numero}"

    def montar_linha_honorarios_fixos(self, dados_cliente):
        incluir = self._bool_from_value(dados_cliente.get('{{INCLUIR_HON_FIXOS}}', True))
        valor = dados_cliente.get('{{HONORARIOS_FIXOS}}', '')
        if not incluir or not valor:
            return ""
        return f"a) Honorários fixos no valor de {valor}."

    def montar_linha_honorarios_exito(self, dados_cliente):
        incluir_exito = self._bool_from_value(dados_cliente.get('{{INCLUIR_HON_EXITO}}', True))
        valor = dados_cliente.get('{{HONORARIOS_EXITO}}', '')
        if not incluir_exito or not valor:
            return ""
        incluir_fixos = self._bool_from_value(dados_cliente.get('{{INCLUIR_HON_FIXOS}}', True))
        valor_fixos = dados_cliente.get('{{HONORARIOS_FIXOS}}', '')
        if incluir_fixos and valor_fixos:
            letra = 'b'
        else:
            letra = 'a'
        return f"{letra}) Honorários de êxito correspondentes a {valor} sobre os valores líquidos efetivamente recebidos pelo(a) CONTRATANTE."

    def _bool_from_value(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)

    def substituir_no_paragrafo(self, paragrafo, substituicoes):
        for placeholder, valor in substituicoes.items():
            if placeholder in paragrafo.text:
                for run in paragrafo.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, str(valor))
                if placeholder in paragrafo.text:
                    paragrafo.text = paragrafo.text.replace(placeholder, str(valor))

    def substituir_no_tabela(self, tabela, substituicoes):
        for linha in tabela.rows:
            for celula in linha.cells:
                for paragrafo in celula.paragraphs:
                    self.substituir_no_paragrafo(paragrafo, substituicoes)

    def substituir_placeholders_docx(self, docx_path, substituicoes):
        doc = Document(docx_path)
        for paragrafo in doc.paragraphs:
            self.substituir_no_paragrafo(paragrafo, substituicoes)
        for tabela in doc.tables:
            self.substituir_no_tabela(tabela, substituicoes)
        for secao in doc.sections:
            if secao.header:
                for paragrafo in secao.header.paragraphs:
                    self.substituir_no_paragrafo(paragrafo, substituicoes)
                for tabela in secao.header.tables:
                    self.substituir_no_tabela(tabela, substituicoes)
            if secao.footer:
                for paragrafo in secao.footer.paragraphs:
                    self.substituir_no_paragrafo(paragrafo, substituicoes)
                for tabela in secao.footer.tables:
                    self.substituir_no_tabela(tabela, substituicoes)
        doc.save(docx_path)

    def gerar_pdf_individual(self, template_path, dados_cliente, output_pdf):
        substituicoes = dados_cliente.copy()
        substituicoes['{{DATA_EXTENSO}}'] = self.data_por_extenso()
        substituicoes['{{FRASE_RG}}'] = self.gerar_frase_rg(dados_cliente.get('{{RG}}', ''))
        substituicoes['{{FRASE_HONORARIOS_FIXOS}}'] = self.montar_linha_honorarios_fixos(dados_cliente)
        substituicoes['{{FRASE_HONORARIOS_EXITO}}'] = self.montar_linha_honorarios_exito(dados_cliente)
        for chave, valor in substituicoes.items():
            if valor is None:
                substituicoes[chave] = ""

        temp_dir = tempfile.mkdtemp()
        temp_docx = os.path.join(temp_dir, "temp.docx")
        shutil.copy2(template_path, temp_docx)

        try:
            self.substituir_placeholders_docx(temp_docx, substituicoes)
            resultado = {"pdf": None, "erro": None}

            def converter():
                try:
                    pythoncom.CoInitialize()
                    word = comtypes.client.CreateObject("Word.Application")
                    word.Visible = False
                    word.DisplayAlerts = False
                    doc = word.Documents.Open(os.path.abspath(temp_docx))
                    doc.SaveAs(os.path.abspath(output_pdf), FileFormat=17)
                    doc.Close()
                    word.Quit()
                    resultado["pdf"] = output_pdf
                except Exception as e:
                    resultado["erro"] = str(e)
                finally:
                    try:
                        pythoncom.CoUninitialize()
                    except:
                        pass

            thread = threading.Thread(target=converter)
            thread.daemon = True
            thread.start()
            thread.join(timeout=45)

            if thread.is_alive():
                raise Exception("Tempo limite excedido (45s). Verifique se o Word não está com pop-up ou travado.")
            if resultado["erro"]:
                raise Exception(resultado["erro"])
            if not resultado["pdf"]:
                raise Exception("Falha na conversão para PDF")
            return output_pdf
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def gerar_kit(self, template_proc, template_cont, dados_cliente, output_pdf):
        if not os.path.exists(template_proc):
            raise FileNotFoundError(f"Template procuração não encontrado: {template_proc}")
        if not os.path.exists(template_cont):
            raise FileNotFoundError(f"Template contrato não encontrado: {template_cont}")

        kit_temp_dir = tempfile.mkdtemp()
        pdf_proc = os.path.join(kit_temp_dir, "procuracao.pdf")
        pdf_cont = os.path.join(kit_temp_dir, "contrato.pdf")

        try:
            self.gerar_pdf_individual(template_proc, dados_cliente, pdf_proc)
            self.gerar_pdf_individual(template_cont, dados_cliente, pdf_cont)
            merger = PyPDF2.PdfMerger()
            merger.append(pdf_proc)
            merger.append(pdf_cont)
            merger.write(output_pdf)
            merger.close()
            return output_pdf
        finally:
            shutil.rmtree(kit_temp_dir, ignore_errors=True)

    def validar_dados(self, dados):
        obrigatorios = ['{{NOME}}', '{{CPF}}']
        faltando = [campo for campo in obrigatorios if not dados.get(campo)]
        return len(faltando) == 0, faltando