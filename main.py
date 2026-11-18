"""Citizen Assist AI - assistente de orientação ao cidadão (terminal)."""

import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))


def caminho(arquivo):
    return os.path.join(PASTA, "data", arquivo)


def main():
    base = BaseConhecimento(caminho("base_conhecimento.json"))
    if not base.carregar():  # lê o JSON e cria os objetos Orientacao
        print("Aviso: a base de conhecimento não foi carregada. "
              "Confira se existe o arquivo data/base_conhecimento.json.")

    assistente = Assistente("Citizen Assist AI", base,
                            caminho("historico.json"),
                            caminho("atendimentos.csv"))
    try:
        assistente.menu_principal()
    except KeyboardInterrupt:
        print("\n\nEncerrando...")
        assistente.sair()


if __name__ == "__main__":
    main()
