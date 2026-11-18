"""Classe Orientacao: guarda os dados de uma orientação e exibe na tela."""


class Orientacao:
    AVISO = "este assistente NÃO é um canal oficial."

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        # Cada atributo corresponde a um campo do registro no JSON.
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave  # lista de textos
        self.resposta = resposta
        self.documentos = documentos          # lista de textos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self):
        """Mostra a orientação completa, com fonte, data e aviso."""
        print(f"\n>> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários:")
        for doc in self.documentos:
            print(f"  - {doc}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(f"Aviso: {self.AVISO}")

    def __str__(self):
        return f"{self.titulo} [{self.categoria}]"
