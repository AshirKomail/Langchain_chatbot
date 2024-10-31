from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import GoogleGenerativeAI
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pickle

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
db = SQLAlchemy(app)

api_key = "AIzaSyDrKmt50SJv-Wgm9vJeR-kkckPFqtBdKuM"
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

class Chat_db(db.Model):
    User_id = db.Column(db.Integer , primary_key = True)
    # conversation_id = db.Column(db.string , nullable = False)
    memory = db.Column(db.LargeBinary , nullable = False)


@app.route("/chat", methods=["POST"])
def chatbot():
    if request.method == "POST":
        try:
            # user Id
            User_id = request.json["User_id"]
            # User Prompt
            query = request.json["query"]
            
            User = Chat_db.query.filter_by(User_id=User_id).first()

            if User:
                llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

                memory = pickle.loads(User.memory)
                
                conversation = ConversationChain(llm=llm, verbose=False, memory=memory)
                model_response = conversation.predict(input=query)
                
                User.memory=pickle.dumps(conversation.memory)
                db.session.commit()
                
                return jsonify({"Ai chatBot": model_response})
         
            else:
                print(f"new user created: {User_id}")
                
                llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
                memory = ConversationBufferMemory()


                conversation = ConversationChain(llm=llm, verbose=False, memory=memory)
                model_response = conversation.predict(input=query)
                
                dumps_memory = pickle.dumps(conversation.memory)

                chat = Chat_db(User_id= User_id, memory= dumps_memory)
                db.session.add(chat)
                db.session.commit()
                # prompt_text =prompts(user_input)
                return jsonify({"Ai chatBot": model_response})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
























#@app.route("/chat", methods=["POST"])
# def chatbot():
#     if request.method == "POST":
#         try:
#             user_input = request.form["User"]
#             # prompt_text =prompts(user_input)
#             model_response = conversation.predict(input=user_input)
#             return jsonify({"Ai chatBot": model_response})
#         except Exception as e:
#             print(f"Error: {e}")
#             return jsonify({"error": str(e)})

# if __name__ == "__main__":

#     app.run(debug=True)