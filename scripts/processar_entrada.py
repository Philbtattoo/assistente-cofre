#!/usr/bin/env python3
"""
Processador automático de notas da pasta Entrada/
Cofre: ~/Documents/Assistente

Regras aplicadas:
- IDEIA: adicionada ao final de ideias.md no formato:
  - [dd/mm] ideia | status: não avaliada
- PROJETO: se o projeto existir em projetos/*.md, atualiza a data e adiciona ao ## Histórico:
  - dd/mm: evento
  Se não existir, registra em ideias.md como proposta de projeto (respeitando a regra de 1 projeto ativo).
- Nota sem identificador explícito: registrada em ideias.md para não perder informação.
- Arquivo movido para Processados/ (com sufixo de timestamp caso já exista homônimo).
- Registro de cada execução em execucoes.log.
"""

import os
import sys
import glob
import shutil
import re
from datetime import datetime

VAULT_DIR = os.path.expanduser("~/Documents/Assistente")
ENTRADA_DIR = os.path.join(VAULT_DIR, "Entrada")
PROCESSADOS_DIR = os.path.join(VAULT_DIR, "Processados")
PROJETOS_DIR = os.path.join(VAULT_DIR, "projetos")
IDEIAS_FILE = os.path.join(VAULT_DIR, "ideias.md")
LOG_FILE = os.path.join(VAULT_DIR, "execucoes.log")


def log(msg):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{agora}] {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linha)
    print(linha.strip())


def registrar_ideia(texto, data_str):
    # Formato obrigatório: - [dd/mm] ideia | status: não avaliada
    linha = f"- [{data_str}] {texto.strip()} | status: não avaliada\n"
    with open(IDEIAS_FILE, "a", encoding="utf-8") as f:
        f.write(linha)


def registrar_projeto(nome_proj, texto, data_str):
    slug = re.sub(r'[^a-zA-Z0-9_\-]', '', nome_proj.lower().replace(" ", "-")).strip()
    caminho_proj = os.path.join(PROJETOS_DIR, f"{slug}.md")
    
    # Se não achou pelo slug direto, busca por arquivos existentes
    if not os.path.exists(caminho_proj):
        arquivos = glob.glob(os.path.join(PROJETOS_DIR, "*.md"))
        for arq in arquivos:
            nome_base = os.path.splitext(os.path.basename(arq))[0].lower()
            if nome_base == slug or slug in nome_base:
                caminho_proj = arq
                break

    if os.path.exists(caminho_proj) and os.path.basename(caminho_proj) != "_modelo.md":
        with open(caminho_proj, "r", encoding="utf-8") as f:
            conteudo = f.read()

        # Atualizar a data da última atualização
        conteudo = re.sub(
            r'(\*\*Última atualização:\*\*).*',
            rf'\1 {data_str}',
            conteudo
        )

        # Adicionar ao histórico
        nova_linha_hist = f"- {data_str}: {texto.strip()}"
        if "## Histórico" in conteudo:
            partes = conteudo.split("## Histórico")
            corpo_hist = partes[1].rstrip()
            novo_hist = f"{corpo_hist}\n{nova_linha_hist}\n"
            conteudo = partes[0] + "## Histórico" + novo_hist
        else:
            conteudo += f"\n\n## Histórico\n{nova_linha_hist}\n"

        with open(caminho_proj, "w", encoding="utf-8") as f:
            f.write(conteudo)
        return True, os.path.basename(caminho_proj)
    else:
        # Se não existe o projeto, manda para ideias para não criar sem aprovação
        registrar_ideia(f"Proposta de projeto ({nome_proj}): {texto}", data_str)
        return False, None


def mover_para_processados(caminho_origem):
    nome_arquivo = os.path.basename(caminho_origem)
    destino = os.path.join(PROCESSADOS_DIR, nome_arquivo)
    
    # Se já existir arquivo com esse nome em Processados/, adiciona timestamp
    if os.path.exists(destino):
        base, ext = os.path.splitext(nome_arquivo)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = os.path.join(PROCESSADOS_DIR, f"{base}_{ts}{ext}")

    shutil.move(caminho_origem, destino)
    return destino


def processar_arquivo(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        linhas = [l.strip() for l in f.readlines() if l.strip()]

    if not linhas:
        # Arquivo vazio
        mover_para_processados(caminho_arquivo)
        return "Arquivo vazio movido"

    data_str = datetime.now().strftime("%d/%m")
    acoes = []

    # Processamento linha a linha ou blocos
    texto_total = "\n".join(linhas)

    # Verifica se há blocos IDEIA: ou PROJETO:
    achou_tag = False

    for linha in linhas:
        if linha.upper().startswith("IDEIA:"):
            achou_tag = True
            conteudo = linha[len("IDEIA:"):].strip()
            if conteudo:
                registrar_ideia(conteudo, data_str)
                acoes.append(f"Ideia registrada: '{conteudo[:30]}...'")
        elif linha.upper().startswith("PROJETO:"):
            achou_tag = True
            resto = linha[len("PROJETO:"):].strip()
            # Formato esperado: PROJETO: nome | atualização  OU  PROJETO: assistente - atualização
            if "|" in resto:
                partes = resto.split("|", 1)
                nome_proj, texto = partes[0].strip(), partes[1].strip()
            elif "-" in resto:
                partes = resto.split("-", 1)
                nome_proj, texto = partes[0].strip(), partes[1].strip()
            else:
                nome_proj = "assistente"
                texto = resto

            atualizou, arq = registrar_projeto(nome_proj, texto, data_str)
            if atualizou:
                acoes.append(f"Projeto '{arq}' atualizado")
            else:
                acoes.append(f"Projeto '{nome_proj}' não existia; registrado como ideia")

    # Se não continha tags IDEIA: ou PROJETO:, registra a primeira linha/título como ideia
    if not achou_tag:
        primeira_linha = linhas[0].lstrip("# ").strip()
        registrar_ideia(primeira_linha, data_str)
        acoes.append(f"Nota sem tag registrada em ideias: '{primeira_linha[:30]}...'")

    mover_para_processados(caminho_arquivo)
    return "; ".join(acoes)


def main():
    if not os.path.exists(ENTRADA_DIR):
        print(f"Diretório de entrada não encontrado: {ENTRADA_DIR}")
        return

    arquivos = glob.glob(os.path.join(ENTRADA_DIR, "*.md"))
    arquivos = [a for a in arquivos if not a.endswith(".tmp")]

    if not arquivos:
        log("Execução concluída: nenhuma nota nova em Entrada/.")
        return

    log(f"Iniciando processamento de {len(arquivos)} nota(s)...")
    for arq in arquivos:
        nome = os.path.basename(arq)
        try:
            res = processar_arquivo(arq)
            log(f"Processado '{nome}': {res}")
        except Exception as e:
            log(f"ERRO ao processar '{nome}': {str(e)}")

    log("Processamento concluído com sucesso.")


if __name__ == "__main__":
    main()
