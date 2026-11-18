# StartCarreira

Assistente de terminal, feito em Python, que orienta **jovens no primeiro emprego** sobre documentos e direitos básicos: Carteira de Trabalho Digital, CPF, título de eleitor, PIS/NIS, FGTS, vale-transporte, holerite, contrato de experiência, pedido de demissão, conta-salário, alistamento militar e outros.

Ele responde só com o que está na base de conhecimento (`data/base_conhecimento.json`), sempre mostrando a **fonte**, a **data de verificação** e o aviso de que **não é um canal oficial**. Não coleta dados pessoais.

> Global Solution 2026.2: Pensamento Computacional e Automação com Python (FIAP) · Desafio CitizenTech

## Integrantes

| Nome | RM |
|------|----|
| Diego de Oliveira Brandão | 569773 |
| Cristhian Henrique Clementino | 574117 |

## Público e problema

**Público:** jovens que estão arrumando o primeiro emprego (a partir de 14 anos, como aprendiz, até jovens adultos).

**Problema:** quem vai começar a trabalhar precisa de vários documentos e cadastros (CPF, carteira de trabalho, conta gov.br, título de eleitor, alistamento militar) e não sabe por onde começar. A informação está espalhada em vários sites, em linguagem técnica, e se mistura com páginas que parecem oficiais e não são. O assistente reúne as orientações em linguagem simples e aponta a fonte oficial de cada uma.

## ODS relacionados

- **ODS 8 – Trabalho decente e crescimento econômico:** facilita a entrada formal no mercado de trabalho (carteira assinada, direitos básicos, Jovem Aprendiz).
- **ODS 10 – Redução das desigualdades:** quem tem menos acesso à informação perde tempo e oportunidades; a orientação é gratuita.
- **ODS 16 – Paz, justiça e instituições eficazes:** acesso à informação pública confiável e transparente, com fonte e data.

## Como executar

Requisitos: Python 3.8 ou superior. Não usa bibliotecas externas.

```bash
git clone https://github.com/CrisRick367/GS2-Pensamento-Computacional-e-Automa-o-com-Python
cd citizen-assist-ai
python main.py
```

Menu principal:

1. Fazer uma pergunta (texto livre)
2. Navegar por categorias
3. Ver indicadores
4. Exportar atendimentos (CSV)
0. Sair (pede uma nota de facilidade de 1 a 5)

Em todas as telas, **0 volta** para a tela anterior.

## Estrutura do projeto

```
citizen-assist-ai/
├── README.md
├── main.py               # cria os objetos e inicia o menu
├── orientacao.py         # classe Orientacao
├── base_conhecimento.py  # classe BaseConhecimento + normalizar()
├── assistente.py         # classe Assistente
└── data/
    ├── base_conhecimento.json   # 19 orientações, 3 categorias
    ├── historico.json           # um dicionário por atendimento
    └── atendimentos.csv         # exportação (gerado pelo programa)
```

Composição das classes: `Assistente` tem uma `BaseConhecimento`, que tem uma lista de objetos `Orientacao`.

## Regra de pontuação usada

A pergunta é normalizada (minúsculas, sem acentos, sem pontuação) e comparada com cada orientação:

| Regra | Pontos |
|-------|--------|
| Cada palavra-chave da orientação que aparece na pergunta | +3 |
| Cada palavra da pergunta com 4 letras ou mais que aparece no título | +1 |

| Melhor pontuação | Resultado |
|------------------|-----------|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| Menos de 3 pontos | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)` da maior para a menor pontuação. Em caso de empate, vence a orientação cujas palavras-chave encontradas somam mais letras (assunto mais específico); se ainda empatar, vale o menor `id`.

**Exemplo:** "Como tirar o título de eleitor?" → a orientação 11 ("Tirar o primeiro título de eleitor") recebe +3 por `tirar o titulo`, +3 por `titulo de eleitor` e +1 para cada uma de `tirar`, `titulo` e `eleitor` no título: **9 pontos, confiança ALTA**.

**Ajustes feitos em relação ao enunciado:**

- As "alternativas" (até 2) só aparecem se tiverem **3 pontos ou mais**, para não sugerir orientações sem relação com a pergunta.
- O **desempate** usa a especificidade das palavras-chave (ver acima) antes do `id`, para que a ficha mais específica apareça primeiro.
- Se o usuário responde **n**, a orientação recusada **não é mostrada de novo** naquele atendimento.
- A normalização também troca `-`, `/`, aspas, `º` e `ª`, para que "e-Título" vire "e titulo" e "13º" vire "13o".
- Palavras-chave são comparadas como palavras inteiras (a normalização coloca espaços nas pontas), então "pis" não casa com "pista".

## Regras de atendimento

- **Dados pessoais:** perguntas com 8 ou mais dígitos ou com `@` são recusadas e **não são registradas**. O assistente nunca pede nome, CPF, telefone ou e-mail.
- **Entradas inválidas:** opção fora da faixa, letras, resposta vazia e s/n inválido nunca encerram o programa.
- **Arquivos:** se `base_conhecimento.json` ou `historico.json` estiverem ausentes ou corrompidos, o programa avisa e continua funcionando.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: data, origem (`pergunta` ou `categoria`), pergunta, id da orientação, se encontrou, se ajudou, tentativas, tempo em segundos e a nota de facilidade (preenchida ao sair). Para o atendimento por pergunta, `pergunta`, `id_orientacao` e `encontrou` se referem à **última tentativa**. Um campo extra, `perguntas_falhas`, guarda as formulações que não resolveram a dúvida; ele é usado para decidir novas palavras-chave. No atendimento por categoria, a pergunta é registrada como `[Categoria] Título da orientação`. O arquivo `data/atendimentos.csv` é gerado com `csv.DictWriter`.

Indicadores calculados: resposta encontrada (%), taxa de acerto: ajudou (%), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (1 a 5) e lista de dúvidas sem solução. O programa também lista as formulações que precisaram ser reescritas, mas acabaram resolvidas.

## Integrações com outras disciplinas

Nenhuma.

## Fontes consultadas

Todas as orientações foram conferidas em fontes oficiais (data da conferência no campo `verificado_em` de cada registro):

- Carteira de Trabalho Digital: <https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho>
- CPF: <https://gov.br/pt-br/servicos/inscrever-no-cpf>
- Conta gov.br: <https://www.gov.br/governodigital/pt-br/conta-gov-br/saiba-mais-sobre-os-niveis-da-conta-govbr/saiba-mais-sobre-os-niveis-da-conta-govbr>
- PIS/NIS (Meu INSS): <https://meu.inss.gov.br>
- Jovem Aprendiz (TRT 4): <https://www.trt4.jus.br/portais/trt4/jovem-aprendiz>
- Registro em carteira (TST): <https://www.tst.jus.br/jornada-de-trabalho>
- Férias (TST): <https://www.tst.jus.br/ferias1>
- 13º salário (TST): <https://www.tst.jus.br/13-salario>
- FGTS: <https://www.fgts.gov.br/Paginas/sobre-o-fgts/visao-geral.aspx>
- Vale-transporte (TRT 4): <https://www.trt4.jus.br/portais/trt4/vales-transporte-e-alimentacao>
- Holerite e contrato de experiência (CLT): <https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm>
- Pedido de demissão e seguro-desemprego (Ministério do Trabalho e Emprego): <https://www.gov.br/trabalho-e-emprego>
- Conta-salário e portabilidade (Caixa): <https://www.caixa.gov.br/voce/salario-na-caixa/paginas/default.aspx>
- Alistamento militar: <https://alistamento.eb.mil.br>
- Título de eleitor, documentos e quitação militar (TSE): <https://www.tse.jus.br/comunicacao/noticias/2026/Marco/eleitor-em-dia-certificado-de-quitacao-militar-para-tirar-o-titulo-e-obrigatorio-apenas-para-os-conscritos>
- e-Título (TSE): <https://www.tse.jus.br/eleitor/servicos/aplicativo-e-titulo-1>
- Regularização e débitos (TSE): <https://www.tse.jus.br/servicos-eleitorais/e-titulo-perguntas-frequentes>
- Segunda via do título (TSE): <https://www.tse.jus.br/comunicacao/noticias/2025/Fevereiro/nao-sei-onde-esta-o-meu-titulo-eleitoral-como-faco-para-recupera-lo>

## Resultado do teste com usuários

| Indicador | Resultado |
|-----------|-----------|
| Pessoas testadas | 3 |
| Atendimentos | 10 |
| Resposta encontrada (%) | 94.4 |
| Taxa de acerto: ajudou (%) | 77.8 |
| Tempo médio para encontrar | 15.6s |
| Tentativas por atendimento | 1.2 |
| Facilidade de uso (1 a 5) | 4 |

**Dúvidas sem solução:**
  - fiz o titulo online mas nao consigo entrar no aplicativo no celular
  - onde consulto meu numero do pis pelo celular
  - nao consigo entrar no gov.br pede reconhecimento facial
Formulações que precisaram ser reescritas (ideias de palavras-chave):
  - baixei o app do governo mas minha conta ta bronze como muda pra prata

**Melhoria feita a partir do teste:** As seguintes perguntas não foram encontradas no 1° teste: "vale-transporte, holerite e descontos, contrato de experiência, pedido de demissão com seguro-desemprego, e conta-salário pra menor" dessa formas passamos de 14 pra 19 orientações, melhorando significativamente o serviço, além disso também incluímos algumas palavras-chave principalmente siglas e termos informais (PIS, NIS, VT, “fui demitido” etc.).

## Limitações

- Só responde o que está na base (19 orientações). Perguntas fora dela caem em "não encontrei".
- A busca compara palavras, não entende o sentido da frase. Erros de digitação, sinônimos e frases muito diferentes das palavras-chave podem não ser encontrados.
- Palavra-chave de uma orientação pode aparecer em outra pergunta e gerar uma resposta que não era a desejada (por exemplo, "perdi" aponta para a segunda via do título).
- As regras mudam. Prazos, taxas e procedimentos devem ser conferidos na fonte oficial antes de agir.
- O bloqueio de dados pessoais segue a regra do enunciado (8 ou mais dígitos no total, ou `@`). Por isso, uma frase natural com idade, ano e valores pode ser recusada por engano. Nomes e outros dados que não tenham dígitos ou `@` não são detectados.
- O tempo medido inclui o tempo que a pessoa leva para digitar e ler.
- A nota de facilidade é uma só por sessão, pedida ao sair, e vale para todos os atendimentos daquela sessão.
- Regras como o desconto de 6% do vale-transporte, a tabela do INSS e os prazos do seguro-desemprego podem mudar; confira na fonte oficial.
- A base não cobre regras específicas para menores de 18 anos na abertura de conta bancária.
- Este assistente **não é um canal oficial** e não substitui o atendimento dos órgãos públicos.

## Vídeo técnico

[COLAR O LINK DO YOUTUBE (não listado)]
