from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
import os

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
class ChatBot:
    def __init__(self):
        # Initialize the ChatGroq model using the provided API key and a specific model.
        
        self.llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")
        self.default_suggestion_system_prompt = "You are a useful assistant that accepts text input in Indonesian and is designed to support the interviewer. Based on the conversation text provided, create up to 5 in-depth follow-up questions using Indonesian. These questions will help the interviewer explore the candidate's experience, problem-solving abilities, or other relevant areas in more depth. Make sure the 2 final questions are questions that are relevant to the topic of conversation and the 3 questions at the beginning to assess how persistent the candidate is based on their answers in the interview based on the following GRIT:"
        
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
        self.generate_format_chain = self.gen_format_template | self.llm
        self.generate_validation_chain = self.gen_validation_template | self.llm

    def generate_suggestion(self, text, additional_prompt=""):
        # Gabungkan prompt default dengan tambahan user
        full_system_prompt = self.default_suggestion_system_prompt + " " + additional_prompt + "and the response must be neatly formatted with new lines and so on."

        # Membuat prompt template secara dinamis
        gen_suggestion_template = ChatPromptTemplate.from_messages(
            [
                ("system", full_system_prompt),  # System message yang sudah diperbarui
                ("human", f"Input:\n{text}\nnPlease analyze this conversation and generate follow-up questions based on the interview flow.")
            ]
        )

        # Buat chain dengan template dinamis
        generate_suggestion_chain = gen_suggestion_template | self.llm
        
        # Invoke chain
        response = generate_suggestion_chain.invoke({'text': text}).content
        return response
    
    def generate_format(self, text):
        # Invoke the suggestion generation chain with the provided text and return the response.
        response = self.generate_format_chain.invoke({'text':text}).content
        return response
    
    def generate_validation(self, text):
        # Invoke the suggestion generation chain with the provided text and return the response.
        response = self.generate_validation_chain.invoke({'text':text}).content
        return response
    
    def determine_category(self, score):
        if score >= 70:
            return "Considered ✅"
        elif 40 <= score < 70:
            return "Bucket List 📌"
        else:
            return "Disconsidered ❌"

    def generate_summary(self, similarity_percentage):
        """Membuat penjelasan dinamis berdasarkan nilai cosine similarity."""
        explanation = f"Teks transkripsi memiliki kemiripan {similarity_percentage}% dengan JobDesc dan JobSpec.\n"

        # Penjelasan lebih spesifik berdasarkan tingkat kecocokan
        if similarity_percentage >= 90:
            explanation += "Teks ini sangat mirip dengan deskripsi pekerjaan, dengan banyak kata kunci dan frasa yang cocok. Kandidat hampir pasti memiliki pengalaman yang sangat relevan."
        elif similarity_percentage >= 80:
            explanation += "Ada banyak kesamaan dalam kata kunci dan konteks pekerjaan. Kandidat kemungkinan memiliki pengalaman yang cocok dengan deskripsi pekerjaan."
        elif similarity_percentage >= 70:
            explanation += "Beberapa bagian teks mencerminkan pekerjaan yang dicari, tetapi ada sedikit perbedaan dalam keterampilan atau tanggung jawab utama."
        elif similarity_percentage >= 60:
            explanation += "Ada beberapa kemiripan dalam konsep utama, tetapi beberapa bagian penting mungkin tidak sepenuhnya cocok."
        elif similarity_percentage >= 50:
            explanation += "Beberapa kata kunci serupa ditemukan, tetapi konteksnya masih cukup berbeda."
        else:
            explanation += "Transkripsi ini memiliki banyak perbedaan dengan job description, sehingga kemungkinan besar tidak sesuai dengan posisi yang dicari."

        return explanation
    
    def cosine_similarity(self, transkripsi, jobdesc, jobspec):
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        # Konversi ke vektor
        emb1 = model.encode(transkripsi, convert_to_tensor=True)
        emb2 = model.encode(jobdesc, convert_to_tensor=True)
        emb3 = model.encode(jobspec, convert_to_tensor=True)

        # Hitung cosine similarity antar pasangan
        similarity_1_2 = util.pytorch_cos_sim(emb1, emb2).item()  # transkripsi vs jobdesc
        similarity_1_3 = util.pytorch_cos_sim(emb1, emb3).item()  # transkripsi vs jobspec
        similarity_2_3 = util.pytorch_cos_sim(emb2, emb3).item()  # jobdesc vs jobspec

        # Hitung rata-rata similarity
        avg_similarity = (similarity_1_2 + similarity_1_3 + similarity_2_3) / 3
        similarity_percentage = round(avg_similarity * 100, 2)

        # Tentukan kategori berdasarkan similarity
        kategori = self.determine_category(similarity_percentage)

        # Generate penjelasan yang lebih dinamis
        summary = self.generate_summary(similarity_percentage)

        return {
            "kecocokan": f"{similarity_percentage}%",
            "kategori": kategori,
            "penjelasan": summary
        }



