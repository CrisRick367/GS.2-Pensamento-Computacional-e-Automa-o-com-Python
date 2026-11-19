import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))


def caminho(arquivo):
    return os.path.join(PASTA, "data", arquivo)


def main():
    base = BaseConhecimento(caminho("base_conhecimento.json"))
    if not base.carregar():
        print("Aviso: a base de conhecimento não foi carregada. "
              "Confira se existe o arquivo data/base_conhecimento.json.")

    assistente = Assistente("SmartCarreiras", base,
                            caminho("historico.json"),
                            caminho("atendimentos.csv"))
    try:
        assistente.menu_principal()
    except KeyboardInterrupt:
        print("\n\nEncerrando...")
        assistente.sair()


if __name__ == "__main__":
    main()
# salario extra de dezembro