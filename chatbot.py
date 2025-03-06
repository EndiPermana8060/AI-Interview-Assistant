from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
import os
import faiss
import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

class FaissVectorDB:
    def __init__(self, dimension=384):
        self.dimension = dimension  
        self.index = faiss.IndexFlatL2(dimension)  
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")
        
        # Dictionary untuk menyimpan metadata (text -> tipe)
        self.text_metadata = {}  
        self.texts = []  # Untuk menyimpan teks asli

    def add_text(self, text1, text2):
        """ Menambahkan dua teks (GRIT, JOBDESC, JOBSPEC) ke FAISS dengan metadata. """
        texts = [text1, text2]
        types = ["JOBDESC", "JOBSPEC"]  # Label masing-masing teks

        vectors = self.model.encode(texts)  

        self.index.add(np.array(vectors, dtype=np.float32))  
        self.texts.extend(texts)  

        # Simpan metadata
        for text, t in zip(texts, types):
            self.text_metadata[t] = text  

        print(f"Dua teks berhasil disimpan dengan metadata:\n"
              f"🔹 GRIT: {text1}\n"
              f"🔹 JOBDESC: {text2}")

    def get_text_by_type(self, text_type):
        """ Mengambil teks berdasarkan tipe (GRIT, JOBDESC, atau JOBSPEC). """
        return self.text_metadata.get(text_type, None)

    def get_vector_by_type(self, text_type):
        """ Mengambil vektor berdasarkan tipe teks. """
        text = self.get_text_by_type(text_type)
        return self.model.encode([text])[0] if text else None


class ChatBot:
    def __init__(self):
        # Initialize the ChatGroq model using the provided API key and a specific model.
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")
        self.vectorizer = TfidfVectorizer()  # TF-IDF untuk keyword search
        self.llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")
        self.default_suggestion_system_prompt = "You are a helpful assistant that receives text input in Indonesian and designed to support interviewers. Given the conversation text provided, generate up to 5 insightful follow-up questions using indonesian language. These questions should help the interviewer explore the candidate's experience, problem-solving abilities, or other relevant areas more deeply. Ensure the questions are relevant, concise, and written in Indonesian to suit the context."
        
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
        self.gen_summary_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an assistant who is an expert in summarizing interview texts in Indonesian. Given the results of an unstructured interview transcription, your task is to create a summary that is clear, concise, and retains key information."
                ),
                (
                    "human",
                    "Input:\n{text}\nPlease make a summary regarding the text which contains unstructured interview conversations from the text."
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
        self.generate_summary_chain = self.gen_summary_template | self.llm

    def generate_suggestion_without_grit(self, text):
        full_system_prompt = self.default_suggestion_system_prompt
        gen_suggestion_without_grit_template = ChatPromptTemplate.from_messages(
            [
                ("system", full_system_prompt),  # System message yang sudah diperbarui
                ("human", f"Input:\n{text}\nnPlease analyze this conversation and generate follow-up questions based on the interview flow.")
            ]
        )

        # Buat chain dengan template dinamis
        generate_suggestion_without_grit_chain = gen_suggestion_without_grit_template | self.llm
        
        # Invoke chain
        response = generate_suggestion_without_grit_chain.invoke({'text': text}).content
        return response

    def generate_suggestion_with_grit(self, text, additional_prompt=""):
        # Gabungkan prompt default dengan tambahan user
        full_system_prompt = self.default_suggestion_system_prompt + "Make sure the questions at the beginning to assess how persistent the candidate is based on their answers in the interview based on the following GRIT: " + additional_prompt + "and the response must be neatly formatted with new lines and so on."

        # Membuat prompt template secara dinamis
        gen_suggestion_with_grit_template = ChatPromptTemplate.from_messages(
            [
                ("system", full_system_prompt),  # System message yang sudah diperbarui
                ("human", f"Input:\n{text}\nnPlease analyze this conversation and generate follow-up questions based on the interview flow.")
            ]
        )

        # Buat chain dengan template dinamis
        generate_suggestion_with_grit_chain = gen_suggestion_with_grit_template | self.llm
        
        # Invoke chain
        response = generate_suggestion_with_grit_chain.invoke({'text': text}).content
        return response
    
    def generate_format(self, text):
        # Invoke the suggestion generation chain with the provided text and return the response.
        response = self.generate_format_chain.invoke({'text':text}).content
        return response
    
    def generate_validation(self, text):
        # Invoke the suggestion generation chain with the provided text and return the response.
        response = self.generate_validation_chain.invoke({'text':text}).content
        return response
    
    def generate_summary(self, text):
        # Invoke the suggestion generation chain with the provided text and return the response.
        response = self.generate_summary_chain.invoke({'text':text}).content
        return response
    
    def determine_category(self, score):
        if score >= 70:
            return "Considered ✅"
        elif 40 <= score < 70:
            return "Bucket List 📌"
        else:
            return "Disconsidered ❌"

    
    def cosine_similarity(self, transkripsi, jobdesc, jobspec):
        # Generate ringkasan transkripsi
        summary = self.generate_summary(transkripsi)

        # Konversi teks ke vektor embedding
        emb1 = self.model.encode(transkripsi, convert_to_tensor=True)
        emb2 = torch.tensor(jobdesc, dtype=torch.float32) if not torch.is_tensor(jobdesc) else jobdesc
        emb3 = torch.tensor(jobspec, dtype=torch.float32) if not torch.is_tensor(jobspec) else jobspec

        # Pastikan dimensi batch sesuai
        emb1 = emb1.unsqueeze(0) if emb1.dim() == 1 else emb1
        emb2 = emb2.unsqueeze(0) if emb2.dim() == 1 else emb2
        emb3 = emb3.unsqueeze(0) if emb3.dim() == 1 else emb3

        # Hitung Cosine Similarity
        similarity_1_2 = util.pytorch_cos_sim(emb1, emb2).mean().item()
        similarity_1_3 = util.pytorch_cos_sim(emb1, emb3).mean().item()
        avg_similarity = (similarity_1_2 + similarity_1_3) / 2

        # Normalisasi skor semantic search
        semantic_score = round(avg_similarity * 100, 2)

        # 🔹 Keyword Search menggunakan TF-IDF
        keyword_score = self.keyword_search(summary, [jobdesc, jobspec])

        # 🔹 Hybrid Score (Gabungan Semantic + Keyword Search)
        hybrid_score = round((0.6 * semantic_score) + (0.4 * keyword_score), 2)

        # Tentukan kategori
        kategori = self.determine_category(hybrid_score)

        # Generate validasi tambahan
        validation = self.generate_validation(transkripsi)

        return {
            "kecocokan": f"{hybrid_score}%",
            "kategori": kategori,
            "penjelasan": summary,
            "validasi": validation
        }

    def keyword_search(self, query, docs):
        """Menggunakan TF-IDF untuk mencari keyword relevance."""
        # 🔹 Pastikan semua dokumen dalam format string
        docs = [str(doc) for doc in docs]  # Konversi list ke string

        corpus = [query] + docs  # Gabungkan query dengan dokumen
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        query_vector = tfidf_matrix[0]  # Vektor query
        doc_vectors = tfidf_matrix[1:]  # Vektor dokumen

        # Hitung kesamaan menggunakan cosine similarity
        keyword_similarities = (query_vector @ doc_vectors.T).toarray().flatten()
        keyword_score = np.mean(keyword_similarities) * 100  # Skala ke 0-100

        return round(keyword_score, 2)
