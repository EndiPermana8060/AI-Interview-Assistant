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
        # Define the prompt template for generating formatted-text.
        self.gen_format_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an assistant that helps structure conversations in Indonesian into a question-and-answer format. Given unstructured conversation text, convert each dialogue into relevant question-and-answer pairs. Ensure the final output is clear, concise, and well-structured in Indonesian."
                ),
                (
                    "human",
                    "Input:\n{text}\nPlease convert this text into a structured question-and-answer format. Ensure that each relevant dialogue is paired into a clear Q&A format."
                )
            ]
        )
        # Define the prompt template for validating arguement.
        self.gen_validation_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an assistant who can validate text conversation in Indonesian, you can give an opinion regarding the statement in the conversation, if the statement is not true then say that the argument is wrong and you give the correct answer, and if the argument is only incomplete that doesn't mean it is wrong, you just add the shortcomings."
                ),
                (
                    "human",
                    "Input:\n{text}\nplease analyze the text then validate whether what is said in the text is wrong or not."
                )
            ]
        )


        # Create a suggestion generation chain by combining the template and the model.
        self.generate_suggestion_chain = self.gen_suggestion_template | self.llm
        self.generate_format_chain = self.gen_format_template | self.llm
        self.generate_validation_chain = self.gen_validation_template | self.llm

    def generate_suggestion(self, text):
        # Invoke the suggestion generation chain with the provided text and return the response.
        response = self.generate_suggestion_chain.invoke({'text':text}).content
        return response
    
    def generate_format(self, text):
        # Invoke the suggestion generation chain with the provided text and return the response.
        response = self.generate_format_chain.invoke({'text':text}).content
        return response
    
    def generate_validation(self, text):
        # Invoke the suggestion generation chain with the provided text and return the response.
        response = self.generate_validation_chain.invoke({'text':text}).content
        return response

