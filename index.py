import json
import os
from datetime import datetime, timedelta

# Arquivos
ARQ_TAREFAS = "tarefas.json"
ARQ_ARQUIVADAS = "tarefas_arquivadas.json"

tarefas = []
proximo_id = 1


# ---------------- UTILITÁRIOS ----------------

def debug(msg):
    print(f"[DEBUG] {msg}")


def carregar_json(arquivo):
    """Carrega um arquivo JSON ou cria caso não exista."""
    if not os.path.exists(arquivo):
        with open(arquivo, "w") as f: json.dump([], f)
    with open(arquivo, "r") as f:
        return json.load(f)


def salvar_json(arquivo, dados):
    """Salva dados no arquivo JSON."""
    with open(arquivo, "w") as f:
        json.dump(dados, f, indent=4)


# ---------------- INICIALIZAÇÃO ----------------

def carregar_sistema():
    """Carrega tarefas e configura próximo ID disponível."""
    global tarefas, proximo_id
    debug("Carregando sistema...")
    tarefas = carregar_json(ARQ_TAREFAS)
    proximo_id = max([t["ID"] for t in tarefas], default=0) + 1


# ---------------- FUNÇÕES PRINCIPAIS ----------------

def criar_tarefa():
    """Cria uma nova tarefa com validações."""
    debug("Executando criar_tarefa")
    global proximo_id

    titulo = input("Título: ").strip()
    if not titulo:
        print("Título obrigatório.")
        return

    descricao = input("Descrição: ")

    prioridades = ["Urgente", "Alta", "Media", "Baixa"]
    prioridade = input(f"Prioridade {prioridades}: ").strip()
    if prioridade not in prioridades:
        print("Prioridade inválida.")
        return

    origens = ["Email", "Telefone", "Chamado"]
    origem = input(f"Origem {origens}: ").strip()
    if origem not in origens:
        print("Origem inválida.")
        return

    tarefa = {
        "ID": proximo_id,
        "Título": titulo,
        "Descrição": descricao,
        "Prioridade": prioridade,
        "Status": "Pendente",
        "Origem": origem,
        "DataCriacao": datetime.now().isoformat(),
        "DataConclusao": None
    }

    tarefas.append(tarefa)
    proximo_id += 1
    print("Tarefa criada!")


def verificar_urgencia():
    """Seleciona a tarefa Pendente de maior prioridade e coloca como 'Fazendo'."""
    debug("Executando verificar_urgencia")

    ordem = ["Urgente", "Alta", "Media", "Baixa"]

    for p in ordem:
        for t in tarefas:
            if t["Prioridade"] == p and t["Status"] == "Pendente":
                t["Status"] = "Fazendo"
                print(f"Tarefa iniciada: {t['Título']} ({p})")
                return

    print("Nenhuma tarefa pendente.")


def atualizar_prioridade():
    """Altera a prioridade de uma tarefa."""
    debug("Executando atualizar_prioridade")

    try:
        idt = int(input("ID: "))
    except:
        print("ID inválido")
        return

    tarefa = next((t for t in tarefas if t["ID"] == idt), None)
    if not tarefa:
        print("Tarefa não encontrada.")
        return

    prioridades = ["Urgente", "Alta", "Media", "Baixa"]
    nova = input(f"Nova prioridade {prioridades}: ")

    if nova not in prioridades:
        print("Inválida.")
        return

    tarefa["Prioridade"] = nova
    print("Prioridade atualizada!")


def concluir_tarefa():
    """Conclui uma tarefa marcada como 'Fazendo'."""
    debug("Executando concluir_tarefa")

    try:
        idt = int(input("ID: "))
    except:
        print("ID inválido")
        return

    tarefa = next((t for t in tarefas if t["ID"] == idt), None)
    if not tarefa:
        print("Não encontrada.")
        return

    if tarefa["Status"] != "Fazendo":
        print("A tarefa deve estar em execução.")
        return

    tarefa["Status"] = "Concluída"
    tarefa["DataConclusao"] = datetime.now().isoformat()
    print("Tarefa concluída!")


def arquivar_antigas():
    """Arquiva tarefas concluídas há mais de 7 dias."""
    debug("Executando arquivar_antigas")

    agora = datetime.now()
    arquivadas = carregar_json(ARQ_ARQUIVADAS)

    for t in tarefas:
        if t["Status"] == "Concluída" and t["DataConclusao"]:
            concluiu = datetime.fromisoformat(t["DataConclusao"])
            if agora - concluiu > timedelta(days=7):
                t["Status"] = "Arquivado"
                arquivadas.append(t)

    salvar_json(ARQ_ARQUIVADAS, arquivadas)
    print("Arquivamento concluído.")


def excluir_tarefa():
    """Exclusão lógica: muda status para Excluída."""
    debug("Executando excluir_tarefa")

    try:
        idt = int(input("ID: "))
    except:
        print("ID inválido")
        return

    tarefa = next((t for t in tarefas if t["ID"] == idt), None)

    if tarefa:
        tarefa["Status"] = "Excluída"
        print("Tarefa excluída (lógico).")
    else:
        print("Não encontrada.")


def formatar_data(iso):
    """Converte data ISO para formato DD/MM/AAAA HH:MM."""
    dt = datetime.fromisoformat(iso)
    return dt.strftime("%d/%m/%Y %H:%M")


def relatorio():
    """Mostra todas tarefas com cálculo de execução."""
    debug("Executando relatorio")

    for t in tarefas:
        print("\n---------------")
        print(f"ID: {t['ID']} - {t['Título']}")
        print(f"Status: {t['Status']}")
        print(f"Prioridade: {t['Prioridade']}")
        print(f"Criada: {formatar_data(t['DataCriacao'])}")

        if t["DataConclusao"]:
            ini = datetime.fromisoformat(t["DataCriacao"])
            fim = datetime.fromisoformat(t["DataConclusao"])

            print(f"Concluída: {formatar_data(t['DataConclusao'])}")

            duracao = fim - ini
            segundos = int(duracao.total_seconds())

            print(f"Duração: {segundos} segundos")
        else:
            print("Ainda não concluída.")



def relatorio_arquivadas():
    """Mostra tarefas arquivadas."""
    debug("Executando relatorio_arquivadas")

    arq = carregar_json(ARQ_ARQUIVADAS)
    if not arq:
        print("Nenhuma arquivada.")
        return

    for t in arq:
        print(f"[ARQUIVADA] ID {t['ID']} - {t['Título']}")


# ---------------- MENU ----------------

def menu():
    """Menu principal do sistema."""
    debug("Executando menu")

    while True:
        print("\n1 Criar tarefa")
        print("2 Verificar urgência")
        print("3 Atualizar prioridade")
        print("4 Concluir tarefa")
        print("5 Arquivar concluídas antigas")
        print("6 Excluir tarefa (lógico)")
        print("7 Relatório completo")
        print("8 Relatório arquivadas")
        print("0 Sair")

        op = input("Opção: ")

        match op:
            case "1": criar_tarefa()
            case "2": verificar_urgencia()
            case "3": atualizar_prioridade()
            case "4": concluir_tarefa()
            case "5": arquivar_antigas()
            case "6": excluir_tarefa()
            case "7": relatorio()
            case "8": relatorio_arquivadas()
            case "0":
                salvar_json(ARQ_TAREFAS, tarefas)
                print("Dados salvos. Saindo...")
                exit()
            case _:
                print("Opção inválida.")


# ---------------- EXECUÇÃO ----------------

carregar_sistema()
menu()
