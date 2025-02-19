from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
class ChatBot:
    def __init__(self):
        # Initialize the ChatGroq model using the provided API key and a specific model.
        
        self.llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")
        
        # Define the prompt template for generating suggestions.
        self.gen_suggestion_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that receives text input in Indonesian and designed to support interviewers. Given the conversation text provided, generate up to 3 insightful follow-up questions using indonesian language. These questions should help the interviewer explore the candidate's experience, problem-solving abilities, or other relevant areas more deeply. Ensure the questions are relevant, concise, and written in Indonesian to suit the context."
                ),
                (
                    "human",
                    "Input:\n{text}\nPlease analyze this conversation and generate follow-up questions based on the interview flow."
                )
            ]
        )



        # Create a suggestion generation chain by combining the template and the model.
        self.generate_suggestion_chain = self.gen_suggestion_template | self.llm

    def generate_suggestion(self, text):
        # Invoke the suggestion generation chain with the provided text and return the response.
        response = self.generate_suggestion_chain.invoke({'text':text}).content
        return response

