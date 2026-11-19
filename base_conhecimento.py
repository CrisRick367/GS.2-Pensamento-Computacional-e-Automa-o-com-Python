import json

from orientacao import Orientacao

CAMPOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em"]

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c",
           "º": "o", "ª": "a"}

SINAIS = "?!.,;:()-/\"'"

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
TAMANHO_MIN_PALAVRA = 4
LIMITE_ALTA = 6
LIMITE_MEDIA = 3


def normalizar(texto):
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"Aviso: arquivo {self.caminho} não encontrado.")
            return False
        except (json.JSONDecodeError, OSError):
            print(f"Aviso: arquivo {self.caminho} está corrompido ou ilegível.")
            return False

        if not isinstance(dados, list):
            print("Aviso: o JSON deve ser uma lista de orientações.")
            return False

        for registro in dados:
            if self._registro_valido(registro):
                self.orientacoes.append(Orientacao(
                    registro["id"], registro["categoria"], registro["titulo"],
                    registro["palavras_chave"], registro["resposta"],
                    registro["documentos"], registro["onde"],
                    registro["fonte"], registro["verificado_em"]))
            else:
                print("Aviso: um registro inválido foi ignorado.")
        return len(self.orientacoes) > 0

    def _registro_valido(self, registro):
        if not isinstance(registro, dict):
            return False
        for campo in CAMPOS:
            if campo not in registro:
                return False
        return (isinstance(registro["palavras_chave"], list)
                and isinstance(registro["documentos"], list))

    def categorias(self):
        lista = []
        for o in self.orientacoes:
            if o.categoria not in lista:
                lista.append(o.categoria)
        return lista

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def _analisar(self, pergunta, orientacao):
        texto = normalizar(pergunta)
        pontos = 0
        especificidade = 0
        for palavra in orientacao.palavras_chave:
            chave = normalizar(palavra)
            if chave.strip() and chave in texto:
                pontos += PONTOS_PALAVRA_CHAVE
                especificidade += len(chave.strip())
        titulo = normalizar(orientacao.titulo)
        for palavra in set(texto.split()):
            if len(palavra) >= TAMANHO_MIN_PALAVRA and f" {palavra} " in titulo:
                pontos += PONTOS_TITULO
        return pontos, especificidade

    def pontuar(self, pergunta, orientacao):
        return self._analisar(pergunta, orientacao)[0]

    def buscar(self, pergunta):
        resultados = []
        for o in self.orientacoes:
            pontos, especificidade = self._analisar(pergunta, o)
            if pontos > 0:
                resultados.append((pontos, especificidade, o))
        resultados.sort(key=lambda t: (-t[0], -t[1], t[2].id))
        return [(pontos, o) for pontos, _, o in resultados]

    @staticmethod
    def confianca(pontos):
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return "NENHUMA"
