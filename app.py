from flask import Flask, render_template, request, jsonify
import ast
import operator
import re

app = Flask(__name__)

# =========================================================
# MEMÓRIA DA NOVAIA
# =========================================================

memoria = {
    "nome": None,
    "gosta": [],
    "nao_gosta": [],
    "assunto": None
}


# =========================================================
# SISTEMA DE CONVERSAS
# =========================================================

conversas = [
    {
        "id": 1,
        "titulo": "Nova conversa",
        "mensagens": []
    }
]

proximo_id = 2


# =========================================================
# CALCULADORA
# =========================================================

def calcular(expressao):
    try:
        expressao = expressao.strip()
        expressao = expressao.replace(",", ".")
        expressao = expressao.replace("×", "*")
        expressao = expressao.replace("÷", "/")
        expressao = expressao.replace("^", "**")

        arvore = ast.parse(expressao, mode="eval")

        operadores = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow
        }

        def resolver(no):

            if isinstance(no, ast.Constant):

                if isinstance(no.value, (int, float)):
                    return no.value

            if isinstance(no, ast.UnaryOp):

                if isinstance(no.op, ast.USub):
                    return -resolver(no.operand)

                if isinstance(no.op, ast.UAdd):
                    return resolver(no.operand)

            if isinstance(no, ast.BinOp):

                esquerda = resolver(no.left)
                direita = resolver(no.right)

                if type(no.op) in operadores:
                    return operadores[type(no.op)](
                        esquerda,
                        direita
                    )

            raise ValueError

        return resolver(arvore.body)

    except Exception:
        return None


def formatar_resultado(resultado):

    if isinstance(resultado, float):

        if resultado.is_integer():
            return str(int(resultado))

        return str(round(resultado, 10))

    return str(resultado)


# =========================================================
# ABREVIAÇÕES
# =========================================================

def normalizar_abreviacoes(texto):

    substituicoes = {

        "vcs": "vocês",
        "vc": "você",
        "oq": "o que",
        "pq": "porque",
        "tbm": "também",
        "tb": "também",
        "blz": "beleza",
        "obg": "obrigado",
        "vlw": "valeu",
        "flw": "falou",
        "dps": "depois",
        "nn": "não",

        "phyton": "python",
        "pyton": "python",
        "pyhton": "python"
    }

    for palavra, substituto in substituicoes.items():

        texto = re.sub(
            r"\b" + re.escape(palavra) + r"\b",
            substituto,
            texto
        )

    return texto


def normalizar_texto(texto):

    texto = texto.lower().strip()

    return normalizar_abreviacoes(texto)


# =========================================================
# MEMÓRIA
# =========================================================

def analisar_memoria(texto):

    resultado = re.search(
        r"eu não gosto de (.+)",
        texto
    )

    if resultado:

        coisa = resultado.group(1).strip()

        if coisa:

            if coisa not in memoria["nao_gosta"]:
                memoria["nao_gosta"].append(coisa)

            return (
                "Entendi! 🧠\n\n"
                f"Vou lembrar que você não gosta de {coisa}."
            )


    resultado = re.search(
        r"eu gosto de (.+)",
        texto
    )

    if resultado:

        coisa = resultado.group(1).strip()

        if coisa:

            if coisa not in memoria["gosta"]:
                memoria["gosta"].append(coisa)

            return (
                "Legal! 😄🧠\n\n"
                f"Vou lembrar que você gosta de {coisa}."
            )

    return None


def responder_memoria(texto):

    if (
        "o que voce lembra de mim" in texto
        or "o que lembra de mim" in texto
        or "o que voce sabe sobre mim" in texto
    ):

        partes = []

        if memoria["nome"]:

            partes.append(
                f"Seu nome é {memoria['nome']}."
            )

        if memoria["gosta"]:

            partes.append(
                "Você gosta de "
                + ", ".join(memoria["gosta"])
                + "."
            )

        if memoria["nao_gosta"]:

            partes.append(
                "Você não gosta de "
                + ", ".join(memoria["nao_gosta"])
                + "."
            )

        if memoria["assunto"]:

            partes.append(
                "Nosso assunto mais recente é "
                f"{memoria['assunto']}."
            )

        if not partes:

            return (
                "Por enquanto ainda não tenho muitas "
                "informações guardadas sobre você. 🧠"
            )

        return (
            "Claro! 🧠🤖\n\n"
            + "\n".join(partes)
        )


    if "do que eu gosto" in texto:

        if memoria["gosta"]:

            return (
                "Você me contou que gosta de "
                + ", ".join(memoria["gosta"])
                + ". 😄"
            )

        return "Você ainda não me contou do que gosta. 😄"


    if "do que eu nao gosto" in texto:

        if memoria["nao_gosta"]:

            return (
                "Você me contou que não gosta de "
                + ", ".join(memoria["nao_gosta"])
                + "."
            )

        return (
            "Você ainda não me contou do que não gosta."
        )

    return None


# =========================================================
# PYTHON
# =========================================================

def resposta_python(texto):

    if "python" not in texto:
        return None


    if (
        "como o python funciona" in texto
        or "como python funciona" in texto
        or "como funciona o python" in texto
        or "como funciona python" in texto
    ):

        return (
            "O Python funciona através de instruções que "
            "você escreve em código. 🐍💻\n\n"
            "Quando você executa um programa, o Python "
            "interpreta essas instruções e realiza as "
            "ações que você programou.\n\n"
            "Por exemplo, você pode escrever uma instrução "
            "para fazer uma conta, guardar uma informação "
            "ou mostrar uma mensagem na tela.\n\n"
            "Na NovaIA, o Python recebe a mensagem que você "
            "envia, analisa as regras do programa e prepara "
            "uma resposta para mostrar no chat."
        )


    if (
        "pra que serve" in texto
        or "para que serve" in texto
        or "serve para que" in texto
        or "usado para" in texto
        or "usada para" in texto
        or "serve pra" in texto
    ):

        return (
            "Python é usado para muitas coisas! 🐍💻\n\n"
            "Ele pode ser usado para criar programas, "
            "sites, automações, servidores, ferramentas, "
            "jogos e projetos de inteligência artificial.\n\n"
            "Também é muito usado para trabalhar com dados "
            "e automatizar tarefas.\n\n"
            "Na NovaIA, usamos Python para fazer a parte "
            "do servidor que recebe suas mensagens e "
            "prepara as respostas."
        )


    if (
        "o que da para fazer" in texto
        or "o que dá para fazer" in texto
        or "o que da pra fazer" in texto
        or "o que dá pra fazer" in texto
        or "o que posso fazer" in texto
        or "o que posso criar" in texto
        or "o que consigo fazer" in texto
    ):

        return (
            "Com Python dá para criar muitos tipos de projetos! 🐍🚀\n\n"
            "Por exemplo: calculadoras, programas, "
            "automações, servidores, ferramentas, jogos "
            "simples e sistemas.\n\n"
            "Python também é muito usado em inteligência "
            "artificial e análise de dados.\n\n"
            "A NovaIA é um exemplo de projeto que estamos "
            "construindo com Python."
        )


    if (
        "o que é python" in texto
        or "o que e python" in texto
        or "me explica python" in texto
    ):

        return (
            "Python 🐍 é uma linguagem de programação "
            "muito usada na tecnologia.\n\n"
            "Com ela podemos criar programas, automações, "
            "servidores, ferramentas e projetos de "
            "inteligência artificial."
        )


    if "exemplo" in texto:

        return (
            "Um exemplo de programa em Python é uma "
            "calculadora. 🧮\n\n"
            "Podemos escrever código para receber números, "
            "fazer uma conta e mostrar o resultado.\n\n"
            "Também podemos usar Python para criar "
            "servidores, ferramentas e sistemas."
        )


    return (
        "Python 🐍 é uma linguagem de programação muito "
        "versátil e usada em várias áreas da tecnologia."
    )


# =========================================================
# PROGRAMAÇÃO
# =========================================================

def resposta_programacao(texto):

    if (
        "pra que serve" in texto
        or "para que serve" in texto
    ):

        return (
            "Programação serve para criar instruções "
            "que fazem o computador realizar tarefas. 💻\n\n"
            "Com ela podemos criar aplicativos, sites, "
            "jogos, sistemas, automações e muito mais."
        )


    if "como funciona" in texto:

        return (
            "Programação funciona através de instruções "
            "que o computador executa. 💻\n\n"
            "O programador escreve essas instruções usando "
            "uma linguagem de programação."
        )


    if (
        "o que é" in texto
        or "o que e" in texto
        or "me explica" in texto
    ):

        return (
            "Programação é o processo de escrever instruções "
            "para um computador executar. 💻"
        )

    return None


# =========================================================
# INTELIGÊNCIA ARTIFICIAL
# =========================================================

def resposta_ia(texto):

    palavras_ia = [
        "inteligência artificial",
        "inteligencia artificial",
        "o que é ia",
        "o que e ia",
        "ia"
    ]

    encontrou = False

    for palavra in palavras_ia:

        if palavra in texto:

            encontrou = True
            break

    if not encontrou:
        return None


    if (
        "o que é inteligência artificial" in texto
        or "o que e inteligencia artificial" in texto
        or "o que é ia" in texto
        or "o que e ia" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "Inteligência Artificial, ou IA, é uma área "
            "da computação que busca criar sistemas capazes "
            "de realizar tarefas que normalmente exigiriam "
            "algum tipo de inteligência humana. 🤖🧠\n\n"
            "Dependendo do sistema, uma IA pode analisar "
            "informações, reconhecer padrões, conversar, "
            "classificar dados ou gerar conteúdos."
        )


    if (
        "pra que serve" in texto
        or "para que serve" in texto
        or "serve para que" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "A inteligência artificial pode ser usada "
            "para muitas tarefas! 🤖\n\n"
            "Ela pode ajudar a analisar informações, "
            "reconhecer padrões, responder perguntas, "
            "ajudar em estudos, automatizar tarefas e "
            "trabalhar com diferentes tipos de conteúdo.\n\n"
            "O que uma IA consegue fazer depende do "
            "modelo e do sistema que foi criado."
        )


    if (
        "como funciona" in texto
        or "como a ia funciona" in texto
        or "como funciona uma ia" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "Uma IA funciona usando modelos computacionais "
            "que processam informações e identificam "
            "padrões para realizar determinadas tarefas. 🧠🤖\n\n"
            "Em sistemas de IA modernos, modelos podem ser "
            "treinados com grandes quantidades de dados "
            "para aprender padrões e produzir resultados.\n\n"
            "O funcionamento exato depende do tipo de IA "
            "e da tarefa que ela foi criada para realizar."
        )


    if (
        "o que da para fazer com ia" in texto
        or "o que dá para fazer com ia" in texto
        or "o que da pra fazer com ia" in texto
        or "o que dá pra fazer com ia" in texto
        or "o que posso fazer com ia" in texto
        or "o que posso criar com ia" in texto
        or "o que consigo fazer com ia" in texto
        or "o que é possível fazer com ia" in texto
        or "o que e possivel fazer com ia" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "Com inteligência artificial dá para fazer "
            "muitas coisas! 🤖🚀\n\n"
            "Por exemplo, podemos criar assistentes virtuais, "
            "gerar e analisar textos, ajudar nos estudos, "
            "analisar informações, reconhecer padrões e "
            "automatizar tarefas.\n\n"
            "Também existem IAs capazes de trabalhar com "
            "imagens, áudio, vídeo e programação.\n\n"
            "O que a IA consegue fazer depende do modelo "
            "e das ferramentas usadas para construir o sistema."
        )


    return (
        "A inteligência artificial é uma área enorme "
        "da tecnologia. 🤖🧠\n\n"
        "Se quiser, posso explicar o que é IA, para que "
        "ela serve ou como ela funciona."
    )


# =========================================================
# MATEMÁTICA
# =========================================================

def resposta_matematica(texto):

    if (
        "o que é uma fração" in texto
        or "o que e uma fracao" in texto
    ):

        return (
            "Uma fração representa uma parte de um todo. 🧮\n\n"
            "Por exemplo, 3/4 significa três partes de um "
            "total dividido em quatro partes iguais.\n\n"
            "O número de cima é o numerador e o número "
            "de baixo é o denominador."
        )


    if (
        "pra que serve" in texto
        or "para que serve" in texto
    ):

        return (
            "A matemática serve para resolver problemas "
            "e entender números, quantidades, formas e relações. 🧮"
        )

    return None


# =========================================================
# CONVERSA
# =========================================================

def resposta_conversa(texto):

    if texto in [
        "oi",
        "olá",
        "ola",
        "oii",
        "oiii",
        "eai",
        "e aí",
        "e ai",
        "hey",
        "hello"
    ]:

        if memoria["nome"]:

            return (
                f"Olá, {memoria['nome']}! 😄\n\n"
                "Que bom te ver novamente!\n\n"
                "Como posso ajudar hoje?"
            )

        return (
            "Olá! 😄\n\n"
            "Eu sou a NovaIA! 🤖\n\n"
            "Como posso ajudar você hoje?"
        )


    if "bom dia" in texto:

        return (
            "Bom dia! ☀️\n\n"
            "Espero que seu dia esteja começando bem!"
        )


    if "boa tarde" in texto:

        return (
            "Boa tarde! 😄\n\n"
            "Como posso ajudar?"
        )


    if "boa noite" in texto:

        return (
            "Boa noite! 🌙\n\n"
            "Espero que você tenha tido um ótimo dia!"
        )


    if (
        "obrigado" in texto
        or "obrigada" in texto
    ):

        return (
            "Por nada! 😄\n\n"
            "Fico feliz em ajudar!"
        )


    if "valeu" in texto:

        return "É nós! 😎🤖"


    if "falou" in texto:

        return "Falou! 👋 Até a próxima!"


    if "beleza" in texto:

        return "Beleza! 😎🤖"


    if "entendi" in texto:

        return (
            "Boa! 😎🧠\n\n"
            "Se quiser continuar esse assunto, "
            "pode mandar outra pergunta."
        )


    if (
        "não entendi" in texto
        or "nao entendi" in texto
    ):

        return (
            "Sem problema! 😄\n\n"
            "Posso explicar de um jeito mais simples "
            "ou dar um exemplo."
        )


    if (
        "seu nome" in texto
        or "como você se chama" in texto
        or "como voce se chama" in texto
    ):

        return (
            "Meu nome é NovaIA! 🤖\n\n"
            "Sou a assistente virtual que estamos "
            "construindo juntos."
        )


    if (
        "quem é você" in texto
        or "quem e voce" in texto
    ):

        return (
            "Eu sou a NovaIA! 🤖🧠\n\n"
            "Sou uma assistente virtual que estamos "
            "desenvolvendo juntos.\n\n"
            "Já consigo conversar, lembrar seu nome, "
            "entender abreviações, resolver contas e "
            "responder perguntas sobre alguns assuntos."
        )


    if "capital do brasil" in texto:

        return "A capital do Brasil é Brasília! 🇧🇷"


    if "piada" in texto:

        return (
            "Claro! 😂\n\n"
            "Por que o computador foi ao médico?\n\n"
            "Porque estava com um vírus! 🖥️😂"
        )


    if "curiosidade" in texto:

        return (
            "Claro! 🧠🌎\n\n"
            "Uma curiosidade interessante é que Vênus "
            "gira em sentido contrário ao da maioria "
            "dos planetas do Sistema Solar."
        )

    return None


# =========================================================
# GERAR RESPOSTA
# =========================================================

def gerar_resposta(mensagem):

    texto = normalizar_texto(mensagem)


    # NOME

    if texto.startswith("meu nome é "):

        nome = mensagem[
            len("meu nome é "):
        ].strip()

        memoria["nome"] = nome

        return (
            f"Prazer em te conhecer, {nome}! 😄\n\n"
            "Agora vou lembrar do seu nome."
        )


    if texto.startswith("meu nome e "):

        nome = mensagem[
            len("meu nome e "):
        ].strip()

        memoria["nome"] = nome

        return (
            f"Prazer em te conhecer, {nome}! 😄"
        )


    if texto.startswith("me chamo "):

        nome = mensagem[
            len("me chamo "):
        ].strip()

        memoria["nome"] = nome

        return (
            f"Prazer em te conhecer, {nome}! 😄"
        )


    if (
        "qual é meu nome" in texto
        or "qual e meu nome" in texto
        or "qual é o meu nome" in texto
        or "qual e o meu nome" in texto
        or "qual meu nome" in texto
        or "como eu me chamo" in texto
    ):

        if memoria["nome"]:

            return (
                f"Seu nome é {memoria['nome']}! 🧠"
            )

        return (
            "Você ainda não me contou seu nome. 😄"
        )


    # MEMÓRIA

    resposta = analisar_memoria(texto)

    if resposta is not None:
        return resposta


    resposta = responder_memoria(texto)

    if resposta is not None:
        return resposta


    # PYTHON

    if "python" in texto:

        resposta = resposta_python(texto)

        if resposta is not None:
            return resposta


    # IA

    if (
        "inteligência artificial" in texto
        or "inteligencia artificial" in texto
        or "o que é ia" in texto
        or "o que e ia" in texto
        or texto == "ia"
    ):

        resposta = resposta_ia(texto)

        if resposta is not None:
            return resposta


    # PROGRAMAÇÃO

    if (
        "programação" in texto
        or "programacao" in texto
        or "programar" in texto
    ):

        resposta = resposta_programacao(texto)

        if resposta is not None:
            return resposta


    # MATEMÁTICA

    if (
        "matemática" in texto
        or "matematica" in texto
        or "fração" in texto
        or "fracao" in texto
    ):

        resposta = resposta_matematica(texto)

        if resposta is not None:
            return resposta


    # CONVERSA

    resposta = resposta_conversa(texto)

    if resposta is not None:
        return resposta


    # CALCULADORA

    expressao = texto

    palavras = [
        "quanto é",
        "quanto e",
        "calcule",
        "calcula",
        "resultado de",
        "qual o resultado de",
        "qual é o resultado de",
        "qual e o resultado de"
    ]

    for palavra in palavras:

        expressao = expressao.replace(
            palavra,
            ""
        )

    expressao = expressao.strip()

    resultado = calcular(expressao)

    if resultado is not None:

        memoria["assunto"] = "matemática"

        return (
            "O resultado é "
            f"{formatar_resultado(resultado)} 🧮"
        )


    # RESPOSTA PADRÃO

    return (
        "Entendi! 🧠\n\n"
        "Ainda estou aprendendo, mas posso "
        "tentar entender se você explicar "
        "um pouco mais."
    )


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route("/")
def inicio():

    return render_template(
        "index.html"
    )


# =========================================================
# LISTAR CONVERSAS
# =========================================================

@app.route("/conversas")
def listar_conversas():

    resultado = []

    for conversa in conversas:

        titulo = conversa["titulo"]

        # Se já tiver mensagens, usa a primeira
        # mensagem como título da conversa.

        if (
            titulo == "Nova conversa"
            and len(conversa["mensagens"]) > 0
        ):

            primeira = conversa["mensagens"][0]

            titulo = primeira["texto"][:30]

            if len(primeira["texto"]) > 30:
                titulo += "..."

        resultado.append({

            "id": conversa["id"],

            "titulo": titulo

        })

    return jsonify(resultado)


# =========================================================
# ABRIR UMA CONVERSA
# =========================================================

@app.route("/conversa/<int:id>")
def abrir_conversa(id):

    for conversa in conversas:

        if conversa["id"] == id:

            return jsonify(conversa)

    return jsonify({
        "erro": "Conversa não encontrada."
    }), 404


# =========================================================
# NOVA CONVERSA
# =========================================================

@app.route("/nova_conversa", methods=["POST"])
def nova_conversa():

    global proximo_id

    nova = {

        "id": proximo_id,

        "titulo": "Nova conversa",

        "mensagens": []

    }

    conversas.append(nova)

    proximo_id += 1

    return jsonify(nova)


# =========================================================
# EXCLUIR CONVERSA
# =========================================================

@app.route(
    "/excluir_conversa/<int:id>",
    methods=["DELETE"]
)
def excluir_conversa(id):

    global conversas


    # Não deixa ficar sem nenhuma conversa.

    if len(conversas) <= 1:

        return jsonify({

            "sucesso": False,

            "mensagem":
                "Você precisa ter pelo menos uma conversa."

        })


    for conversa in conversas:

        if conversa["id"] == id:

            conversas.remove(conversa)

            return jsonify({

                "sucesso": True

            })


    return jsonify({

        "sucesso": False,

        "mensagem": "Conversa não encontrada."

    }), 404


# =========================================================
# CHAT
# =========================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    dados = request.get_json()

    mensagem = dados.get(
        "mensagem",
        ""
    ).strip()


    if not mensagem:

        return jsonify({

            "resposta":
                "Digite alguma coisa para conversar comigo. 😄"

        })


    conversa_id = dados.get(
        "conversa_id",
        1
    )


    conversa_encontrada = None


    for conversa in conversas:

        if conversa["id"] == conversa_id:

            conversa_encontrada = conversa

            break


    # Se não encontrar, usa a primeira conversa.

    if conversa_encontrada is None:

        conversa_encontrada = conversas[0]


    # Guarda mensagem do usuário.

    conversa_encontrada["mensagens"].append({

        "tipo": "usuario",

        "texto": mensagem

    })


    # Cria título automaticamente.

    if (
        conversa_encontrada["titulo"]
        == "Nova conversa"
    ):

        titulo = mensagem[:30]

        if len(mensagem) > 30:
            titulo += "..."

        conversa_encontrada["titulo"] = titulo


    # Gera resposta.

    resposta = gerar_resposta(
        mensagem
    )


    # Guarda resposta da NovaIA.

    conversa_encontrada["mensagens"].append({

        "tipo": "ia",

        "texto": resposta

    })


    return jsonify({

        "resposta": resposta,

        "conversa_id":
            conversa_encontrada["id"]

    })


# =========================================================
# INICIAR SERVIDOR
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )