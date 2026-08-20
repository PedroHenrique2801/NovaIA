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


def tentar_calcular_frase(texto):

    expressao = texto.lower().strip()

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

    return None

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

                memoria["nao_gosta"].append(
                    coisa
                )

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

                memoria["gosta"].append(
                    coisa
                )

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

        return (
            "Você ainda não me contou do que gosta. 😄"
        )

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
        "o que é python" in texto
        or "o que e python" in texto
        or "me explica python" in texto
    ):

        return (
            "Python 🐍 é uma linguagem de programação "
            "muito usada na tecnologia.\n\n"
            "Com ela podemos criar programas, automações, "
            "servidores, ferramentas, jogos e projetos "
            "de inteligência artificial."
        )

    if (
        "como funciona o python" in texto
        or "como o python funciona" in texto
        or "como funciona python" in texto
    ):

        return (
            "Python funciona através de instruções "
            "escritas em código. 🐍💻\n\n"
            "O computador executa essas instruções "
            "para realizar as tarefas programadas."
        )

    if (
        "pra que serve" in texto
        or "para que serve" in texto
        or "serve para que" in texto
    ):

        return (
            "Python pode ser usado para criar programas, "
            "sites, servidores, automações, jogos, "
            "ferramentas e sistemas de inteligência artificial. 🐍"
        )

    return (
        "Python 🐍 é uma linguagem de programação "
        "muito versátil e usada em várias áreas."
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
            "Com programação podemos criar aplicativos, "
            "sites, jogos, sistemas e automações."
        )

    if "como funciona" in texto:

        return (
            "Programação funciona através de instruções "
            "que o computador executa. 💻\n\n"
            "O programador escreve essas instruções "
            "usando uma linguagem de programação."
        )

    if (
        "o que é" in texto
        or "o que e" in texto
        or "me explica" in texto
    ):

        return (
            "Programação é o processo de escrever "
            "instruções para um computador executar. 💻"
        )

    return None

# =========================================================
# INTELIGÊNCIA ARTIFICIAL
# =========================================================

def resposta_ia(texto):

    if (
        "o que é inteligência artificial" in texto
        or "o que e inteligencia artificial" in texto
        or "o que é ia" in texto
        or "o que e ia" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "Inteligência Artificial, ou IA, é uma área "
            "da computação que cria sistemas capazes "
            "de realizar tarefas de forma inteligente. 🤖🧠\n\n"
            "Algumas IAs conseguem conversar, analisar "
            "informações, reconhecer padrões e ajudar "
            "em várias tarefas."
        )

    if (
        "pra que serve" in texto
        or "para que serve" in texto
        or "serve para que" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "A inteligência artificial pode ajudar em "
            "estudos, análise de informações, programação, "
            "automação e muitas outras tarefas. 🤖"
        )

    if (
        "como funciona" in texto
        or "como a ia funciona" in texto
        or "como funciona uma ia" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "Uma IA usa modelos computacionais que "
            "processam informações e identificam padrões. 🧠🤖\n\n"
            "Muitos sistemas modernos são treinados "
            "com grandes quantidades de dados."
        )

    return (
        "A inteligência artificial é uma área enorme "
        "da tecnologia. 🤖🧠"
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
            "Em 3/4, o 3 é o numerador e o 4 é o denominador."
        )

    if (
        "porcentagem" in texto
        or "percentual" in texto
    ):

        return (
            "Porcentagem representa uma parte de 100. 🧮\n\n"
            "Por exemplo, 50% significa 50 de cada 100."
        )

    if (
        "potência" in texto
        or "potencia" in texto
    ):

        return (
            "Potência é uma multiplicação repetida. 🧮\n\n"
            "Por exemplo, 2³ significa 2 × 2 × 2, "
            "que resulta em 8."
        )

    if (
        "pra que serve" in texto
        or "para que serve" in texto
    ):

        return (
            "A matemática ajuda a resolver problemas "
            "e entender números, quantidades, formas "
            "e relações. 🧮"
        )

    return None

# =========================================================
# HISTÓRIA
# =========================================================

def resposta_historia(texto):

    if (
        "história" not in texto
        and "historia" not in texto
    ):

        return None

    if "segunda guerra mundial" in texto:

        return (
            "A Segunda Guerra Mundial aconteceu entre "
            "1939 e 1945. 🌎📚\n\n"
            "Foi um grande conflito que envolveu "
            "vários países."
        )

    if "independência do brasil" in texto:

        return (
            "A Independência do Brasil foi declarada "
            "em 7 de setembro de 1822. 🇧🇷📚"
        )

    if (
        "o que é história" in texto
        or "o que e historia" in texto
    ):

        return (
            "História é o estudo das sociedades e "
            "dos acontecimentos do passado. 📚"
        )

    return (
        "História estuda acontecimentos e sociedades "
        "do passado. 📚\n\n"
        "Você pode perguntar sobre um acontecimento "
        "histórico específico."
    )

# =========================================================
# GEOGRAFIA
# =========================================================

def resposta_geografia(texto):

    palavras = [
        "geografia",
        "continente",
        "oceano",
        "capital",
        "país",
        "pais"
    ]

    if not any(
        palavra in texto
        for palavra in palavras
    ):

        return None

    if "capital do brasil" in texto:

        return "A capital do Brasil é Brasília! 🇧🇷"

    if "maior país do mundo" in texto:

        return (
            "O maior país do mundo em área "
            "é a Rússia. 🌎"
        )

    if "maior continente" in texto:

        return (
            "O maior continente em área é a Ásia. 🌏"
        )

    if "maior oceano" in texto:

        return (
            "O maior oceano da Terra é o Oceano Pacífico. 🌊"
        )

    if (
        "o que é geografia" in texto
        or "o que e geografia" in texto
    ):

        return (
            "Geografia é o estudo do espaço terrestre, "
            "dos lugares, do clima, do relevo, da população "
            "e de outros aspectos da Terra. 🌎"
        )

    return (
        "Geografia estuda a Terra e a relação entre "
        "as pessoas e os lugares. 🌎"
    )

# =========================================================
# CIÊNCIAS
# =========================================================

def resposta_ciencias(texto):

    palavras = [
        "ciência",
        "ciencia",
        "planeta",
        "terra",
        "sol",
        "lua",
        "gravidade",
        "átomo",
        "atomo",
        "corpo humano"
    ]

    if not any(
        palavra in texto
        for palavra in palavras
    ):

        return None

    if "gravidade" in texto:

        return (
            "A gravidade é uma força que atrai objetos "
            "que possuem massa. 🌎🧲\n\n"
            "É ela que ajuda a manter os objetos "
            "próximos à superfície da Terra."
        )

    if (
        "planeta" in texto
        and "sistema solar" in texto
    ):

        return (
            "O Sistema Solar possui oito planetas "
            "que orbitam o Sol. ☀️🪐"
        )

    if (
        "sol" in texto
        and "estrela" in texto
    ):

        return (
            "Sim! ☀️ O Sol é uma estrela localizada "
            "no centro do Sistema Solar."
        )

    if (
        "o que é ciência" in texto
        or "o que e ciencia" in texto
    ):

        return (
            "Ciência é uma forma de estudar e entender "
            "o mundo usando observações, perguntas, "
            "experimentos e evidências. 🔬"
        )

    return (
        "Ciência ajuda a entender como o mundo "
        "e o universo funcionam. 🔬🧠"
    )

# =========================================================
# INGLÊS
# =========================================================

def resposta_ingles(texto):

    if (
        "como fala" not in texto
        and "como se diz" not in texto
        and "inglês" not in texto
        and "ingles" not in texto
    ):

        return None

    traducoes = {

        "bom dia": "Good morning.",
        "boa noite": "Good night.",
        "obrigado": "Thank you.",
        "por favor": "Please.",
        "olá": "Hello.",
        "ola": "Hello.",
        "tchau": "Goodbye.",
        "amigo": "Friend.",
        "casa": "House.",
        "água": "Water.",
        "agua": "Water.",
        "comida": "Food."
    }

    for portugues, ingles in traducoes.items():

        if portugues in texto:

            return (
                f"Em inglês, '{portugues}' é "
                f"'{ingles}' 🇺🇸"
            )

    if (
        "o que é inglês" in texto
        or "o que e ingles" in texto
    ):

        return (
            "Inglês é uma língua falada em muitos "
            "países e muito usada para comunicação "
            "internacional. 🇺🇸"
        )

    return (
        "Posso ajudar com inglês! 🇺🇸\n\n"
        "Por exemplo, pergunte: "
        "'como fala água em inglês?'"
    )

# =========================================================
# RESPOSTAS EXTRAS
# =========================================================

def resposta_extra(texto):

    if (
        "quem criou você" in texto
        or "quem criou voce" in texto
    ):

        return (
            "Eu fui criada através de código! 🤖💻\n\n"
            "E você está desenvolvendo a NovaIA comigo."
        )

    if (
        "você é uma ia" in texto
        or "voce e uma ia" in texto
    ):

        return (
            "Sim! 🤖\n\n"
            "Eu sou a NovaIA, uma assistente virtual "
            "que estamos construindo com Python."
        )

    if (
        "você é inteligente" in texto
        or "voce e inteligente" in texto
    ):

        return (
            "Estou ficando cada vez melhor! 😎🧠\n\n"
            "Já consigo conversar, lembrar informações, "
            "fazer contas e responder perguntas sobre "
            "vários assuntos."
        )

    if (
        "me ajuda" in texto
        or "me ajude" in texto
    ):

        return (
            "Claro! 😄🤖\n\n"
            "Pode me falar o que você precisa."
        )

    if "tudo bem" in texto:

        return (
            "Tudo certo por aqui! 😎🤖\n\n"
            "E com você?"
        )

    if (
        "você está aí" in texto
        or "voce esta ai" in texto
    ):

        return "Estou aqui! 🤖😎 Pode mandar."

    if (
        "você sabe meu nome" in texto
        or "voce sabe meu nome" in texto
    ):

        if memoria["nome"]:

            return (
                f"Sei sim! Seu nome é "
                f"{memoria['nome']}! 🧠"
            )

        return (
            "Ainda não. Me diga seu nome "
            "que eu posso lembrar."
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
            "Já consigo conversar, lembrar informações, "
            "entender abreviações, resolver contas e "
            "responder perguntas sobre vários assuntos."
        )

    if "piada" in texto:

        return (
            "Claro! 😂\n\n"
            "Por que o computador foi ao médico?\n\n"
            "Porque estava com um vírus! 🖥️😂"
        )

    if "curiosidade" in texto:

        return (
            "Claro! 🧠🌎\n\n"
            "Vênus gira em sentido contrário ao da "
            "maioria dos planetas do Sistema Solar."
        )

    return None

# =========================================================
# GERAR RESPOSTA
# =========================================================

def gerar_resposta(mensagem):

    texto = normalizar_texto(mensagem)

    # -----------------------------------------------------
    # NOME
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CALCULADORA PRIMEIRO
    # -----------------------------------------------------

    resposta = tentar_calcular_frase(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # MEMÓRIA
    # -----------------------------------------------------

    resposta = analisar_memoria(texto)

    if resposta is not None:
        return resposta

    resposta = responder_memoria(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # PYTHON
    # -----------------------------------------------------

    if "python" in texto:

        resposta = resposta_python(texto)

        if resposta is not None:
            return resposta

    # -----------------------------------------------------
    # IA
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # PROGRAMAÇÃO
    # -----------------------------------------------------

    if (
        "programação" in texto
        or "programacao" in texto
        or "programar" in texto
    ):

        resposta = resposta_programacao(texto)

        if resposta is not None:
            return resposta

    # -----------------------------------------------------
    # MATEMÁTICA
    # -----------------------------------------------------

    if (
        "matemática" in texto
        or "matematica" in texto
        or "fração" in texto
        or "fracao" in texto
        or "porcentagem" in texto
        or "potência" in texto
        or "potencia" in texto
    ):

        resposta = resposta_matematica(texto)

        if resposta is not None:
            return resposta

    # -----------------------------------------------------
    # HISTÓRIA
    # -----------------------------------------------------

    resposta = resposta_historia(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # GEOGRAFIA
    # -----------------------------------------------------

    resposta = resposta_geografia(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # CIÊNCIAS
    # -----------------------------------------------------

    resposta = resposta_ciencias(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # INGLÊS
    # -----------------------------------------------------

    resposta = resposta_ingles(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # EXTRAS
    # -----------------------------------------------------

    resposta = resposta_extra(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # CONVERSA
    # -----------------------------------------------------

    resposta = resposta_conversa(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # RESPOSTA PADRÃO
    # -----------------------------------------------------

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
# ABRIR CONVERSA
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

@app.route(
    "/nova_conversa",
    methods=["POST"]
)
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

        "mensagem":
            "Conversa não encontrada."

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

    if conversa_encontrada is None:

        conversa_encontrada = conversas[0]

    conversa_encontrada["mensagens"].append({

        "tipo": "usuario",

        "texto": mensagem

    })

    if (
        conversa_encontrada["titulo"]
        == "Nova conversa"
    ):

        titulo = mensagem[:30]

        if len(mensagem) > 30:

            titulo += "..."

        conversa_encontrada["titulo"] = titulo

    resposta = gerar_resposta(
        mensagem
    )

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