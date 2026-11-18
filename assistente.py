"""Classe Assistente: atendimento, histórico, indicadores e exportação CSV."""

import csv
import json
import time
from datetime import datetime

from base_conhecimento import BaseConhecimento, LIMITE_MEDIA

CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_segundos", "nota_facilidade",
              "perguntas_falhas"]


def ler(texto):
    """input() que não derruba o programa se a entrada acabar (Ctrl+D)."""
    try:
        return input(texto).strip()
    except EOFError:
        return "0"


def tem_dado_pessoal(texto):
    """Bloqueia 8 ou mais dígitos (CPF, telefone) ou o símbolo @ (e-mail)."""
    digitos = sum(1 for c in texto if c.isdigit())
    return digitos >= 8 or "@" in texto


class Assistente:
    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.historico = self._carregar_historico()
        self.inicio_sessao = len(self.historico)  # onde começam os desta sessão

    # ---------- histórico ----------
    def _carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if isinstance(dados, list):
                return [d for d in dados if isinstance(d, dict)]
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, OSError):
            print("Aviso: histórico ilegível. Começando um histórico novo.")
        return []

    def _salvar_historico(self):
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não foi possível salvar o histórico.")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo, perguntas_falhas=None):
        """Guarda um atendimento (dicionário) no histórico e no arquivo.

        pergunta, id_orientacao e encontrou descrevem a ÚLTIMA tentativa.
        perguntas_falhas guarda as formulações que não resolveram a dúvida
        (não encontradas ou recusadas com "n"), para melhorar a base depois.
        """
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,               # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "nota_facilidade": "",
            "perguntas_falhas": perguntas_falhas or [],
        }
        self.historico.append(atendimento)
        self._salvar_historico()

    # ---------- entradas ----------
    def ler_numero(self, texto, minimo, maximo):
        """Pede um número até o usuário digitar um valor válido."""
        while True:
            entrada = ler(texto)
            if entrada.isdigit() and minimo <= int(entrada) <= maximo:
                return int(entrada)
            print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")

    def ler_sim_nao(self, texto):
        while True:
            entrada = ler(texto).lower()
            if entrada in ("s", "n"):
                return entrada == "s"
            print("Resposta inválida. Digite s ou n.")

    # ---------- atendimento por pergunta ----------
    def perguntar(self):
        inicio = time.time()
        tentativas = 0
        ajudou = False
        ultima = ""          # texto da última tentativa
        ultimo_id = None     # orientação exibida na última tentativa (ou None)
        falhas = []          # formulações que não resolveram a dúvida
        rejeitados = set()   # ids que o usuário respondeu "n"

        while True:
            texto = ler("\nDigite sua dúvida (0 para voltar): ")
            if texto == "0":
                break
            if texto == "":
                print("Você não digitou nada. Escreva sua dúvida.")
                continue
            if tem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue  # não registra, não conta tentativa

            tentativas += 1
            ultima = texto
            ultimo_id = None  # cada tentativa começa sem orientação
            # não mostra de novo uma orientação que o usuário já rejeitou
            resultados = [(p, o) for p, o in self.base.buscar(texto)
                          if o.id not in rejeitados]

            if not resultados or resultados[0][0] < LIMITE_MEDIA:
                falhas.append(texto)
                self._nao_encontrei(bool(rejeitados))
                continue

            pontos, melhor = resultados[0]
            ultimo_id = melhor.id
            print(f"\nConfiança da resposta: "
                  f"{BaseConhecimento.confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()

            alternativas = [o for p, o in resultados[1:3] if p >= LIMITE_MEDIA]
            if alternativas:
                print("\nVeja também:")
                for o in alternativas:
                    print(f"  - {o}")

            if self.ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                ajudou = True
                break
            rejeitados.add(melhor.id)
            falhas.append(texto)
            print("Tente reescrever com outras palavras, "
                  "ou digite 0 e use a navegação por categorias.")

        if tentativas > 0:
            tempo = round(time.time() - inicio, 1)
            self.registrar("pergunta", ultima, ultimo_id, ultimo_id is not None,
                           ajudou, tentativas, tempo, falhas)

    def _nao_encontrei(self, ja_mostrou=False):
        print("\nNão encontrei uma orientação para essa dúvida.")
        if ja_mostrou:
            print("(As orientações que você recusou não são mostradas de novo.)")
        print("Tente outras palavras (ex.: cpf, título, carteira de trabalho)")
        print("ou use a navegação por categorias. Categorias disponíveis:")
        for cat in self.base.categorias():
            print(f"  - {cat}")

    # ---------- navegação por categorias ----------
    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("\nA base de conhecimento está vazia.")
            return
        while True:
            print("\n=== Categorias ===")
            for i, cat in enumerate(categorias, start=1):
                print(f"{i}. {cat}")
            print("0. Voltar")
            op = self.ler_numero("Escolha: ", 0, len(categorias))
            if op == 0:
                return
            self._navegar_orientacoes(categorias[op - 1])

    def _navegar_orientacoes(self, categoria):
        lista = self.base.por_categoria(categoria)
        while True:
            inicio = time.time()
            print(f"\n=== {categoria} ===")
            for i, o in enumerate(lista, start=1):
                print(f"{i}. {o.titulo}")
            print("0. Voltar")
            op = self.ler_numero("Escolha: ", 0, len(lista))
            if op == 0:
                return
            orientacao = lista[op - 1]
            orientacao.exibir()
            ajudou = self.ler_sim_nao(
                "\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            descricao = f"[{categoria}] {orientacao.titulo}"
            self.registrar("categoria", descricao, orientacao.id, True,
                           ajudou, 1, tempo, [] if ajudou else [descricao])

    # ---------- indicadores ----------
    def indicadores(self):
        """Calcula os indicadores a partir do histórico e devolve um dicionário."""
        total = len(self.historico)
        if total == 0:
            return None
        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudados = [a for a in self.historico if a.get("ajudou")]
        tempos = [a.get("tempo_segundos", 0) for a in encontrados]
        tentativas = [a.get("tentativas", 1) for a in self.historico]
        notas = [a["nota_facilidade"] for a in self.historico
                 if isinstance(a.get("nota_facilidade"), int)]
        sem_solucao = []   # atendimentos em que a pessoa NÃO foi ajudada
        reescritas = []    # formulações que falharam, mas a dúvida foi resolvida
        for a in self.historico:
            falhas = a.get("perguntas_falhas") or []
            if not a.get("ajudou"):
                lista = falhas or ([a["pergunta"]] if a.get("pergunta") else [])
                destino = sem_solucao
            else:
                lista = falhas
                destino = reescritas
            for p in lista:
                if p not in destino:
                    destino.append(p)
        return {
            "total": total,
            "encontrada_pct": round(100 * len(encontrados) / total, 1),
            "acerto_pct": round(100 * len(ajudados) / total, 1),
            "tempo_medio": round(sum(tempos) / len(tempos), 1) if tempos else 0,
            "tentativas_media": round(sum(tentativas) / total, 1),
            "facilidade": round(sum(notas) / len(notas), 1) if notas else None,
            "sem_solucao": sem_solucao,
            "reescritas": reescritas,
        }

    def exibir_indicadores(self):
        ind = self.indicadores()
        print("\n=== Indicadores ===")
        if ind is None:
            print("Ainda não há atendimentos registrados.")
            return
        print(f"Atendimentos: {ind['total']}")
        print(f"Resposta encontrada (%): {ind['encontrada_pct']}")
        print(f"Taxa de acerto: ajudou (%): {ind['acerto_pct']}")
        print(f"Tempo médio para encontrar: {ind['tempo_medio']} s")
        print(f"Tentativas por atendimento: {ind['tentativas_media']}")
        nota = ind["facilidade"] if ind["facilidade"] is not None else "sem notas"
        print(f"Facilidade de uso (1 a 5): {nota}")
        print("Dúvidas sem solução:")
        if ind["sem_solucao"]:
            for p in ind["sem_solucao"]:
                print(f"  - {p}")
        else:
            print("  (nenhuma)")
        if ind["reescritas"]:
            print("Formulações que precisaram ser reescritas (ideias de "
                  "palavras-chave):")
            for p in ind["reescritas"]:
                print(f"  - {p}")

    # ---------- CSV ----------
    def exportar_csv(self):
        try:
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as f:
                escritor = csv.DictWriter(f, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore")
                escritor.writeheader()
                for a in self.historico:
                    linha = dict(a)
                    linha["perguntas_falhas"] = " | ".join(
                        a.get("perguntas_falhas") or [])
                    escritor.writerow(linha)
            print(f"\nCSV exportado em {self.caminho_csv} "
                  f"({len(self.historico)} atendimentos).")
        except OSError:
            print("Aviso: não foi possível exportar o CSV.")

    # ---------- menu ----------
    def menu_principal(self):
        print(f"\n=== {self.nome} ===")
        print("Orientações para jovens no primeiro emprego.")
        print("Aviso: este assistente NÃO é um canal oficial.")
        print("Nunca digite nome, CPF, telefone ou e-mail.")
        while True:
            print("\n--- Menu ---")
            print("1. Fazer uma pergunta")
            print("2. Navegar por categorias")
            print("3. Ver indicadores")
            print("4. Exportar atendimentos (CSV)")
            print("0. Sair")
            op = self.ler_numero("Escolha: ", 0, 4)
            if op == 1:
                self.perguntar()
            elif op == 2:
                self.navegar()
            elif op == 3:
                self.exibir_indicadores()
            elif op == 4:
                self.exportar_csv()
            else:
                self.sair()
                return

    def sair(self):
        """Pede a nota de facilidade, salva tudo e se despede."""
        if len(self.historico) > self.inicio_sessao:
            while True:
                entrada = ler("\nDe 1 a 5, quão fácil foi usar o assistente? "
                              "(0 para pular): ")
                if entrada.isdigit() and 0 <= int(entrada) <= 5:
                    break
                print("Nota inválida. Digite um número de 1 a 5 (ou 0).")
            if int(entrada) > 0:
                for a in self.historico[self.inicio_sessao:]:
                    a["nota_facilidade"] = int(entrada)
                self._salvar_historico()
        self.exportar_csv()
        self.exibir_indicadores()
        print("\nObrigado por usar o assistente. Até logo!")
