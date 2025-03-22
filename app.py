from flask import Flask, render_template, request
import google.generativeai as genai

from dotenv import load_dotenv
import os

API_KEY = os.getenv("API_KEY")

load_dotenv()

app = Flask(__name__)

# Configurar a API do Google Generative AI
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-pro")
chat = model.start_chat(history=[])

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        mensagem = request.form["pergunta"].strip()

        if mensagem.lower() == "sair":
            resultado = "Conversa encerrada. Até a próxima!"
        else:
            # Prompt base para orientar o modelo
            prompt = f"""
            Você é um especialista personal trainer. Ajude o usuário a montar um treino ideal ou responda dúvidas com base no que ele digitar.
            Se o usuário fornecer informações como biotipo (Ectomorfo, Mesomorfo, Endomorfo), periodização (1, 3, 5 dias) e objetivo (Ganhar massa muscular, Perder peso), crie um treino seguindo estas regras:
            - Biotipo: Ectomorfo (magro, difícil ganhar massa), Mesomorfo (músculos definidos, fácil ganhar massa), Endomorfo (mais gordura, fácil ganhar massa).
            - Periodização: 1 dia (full body), 3 dias (ABC), 5 dias (ABCDE).
            - Tipos de treino: Funcional, Maquinário, Peso Livre, Cardio, HIIT.
            Responda de forma clara e adaptada ao que o usuário digitar. Se precisar de mais informações, peça ao usuário.
            Mensagem do usuário: {mensagem}
            """

            try:
                response = chat.send_message(prompt)
                resultado = response.text
            except Exception as e:
                resultado = f"Erro ao gerar resposta: {e}"
                try:
                    # Fallback para outro modelo
                    fallback_model = genai.GenerativeModel("models/gemini-1.5-flash")
                    fallback_chat = fallback_model.start_chat(history=[])
                    response = fallback_chat.send_message(prompt)
                    resultado = response.text
                except Exception as e2:
                    resultado = f"Erro com o segundo modelo: {e2}"

    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)