import os
import re
import emoji
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from langchain_nebius import ChatNebius

class Article():
    def __init__(self, content=None, source=None):
        self.content = content
        self.source = source

class bio_assistent():
    def __init__(self, chunk_size=1000, chunk_overlap=100):
        self.embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self.generate_model = ChatNebius(
            api_key=os.getenv("NEBIUS_API_KEY"),
            model="Qwen/Qwen3-235B-A22B-Instruct-2507",
            temperature=0.1,
            top_p=0.95
            )
        self.chunk_size = chunk_size
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                            chunk_overlap=chunk_overlap, 
                                                            separators=["\n\n", "\n", " ", ".", "?", "!"],
                                                            keep_separator=True)
        self.vec_db_client = chromadb.PersistentClient(path="../../store/Chroma")
        self.collection = self.vec_db_client.get_or_create_collection("bio_articles")

    def split_article(self, atricle):
        total = 0
        result = []
        for chunk_id, chunk in enumerate(self.text_splitter.split_text(atricle.content)):
            result.append({
                "content": chunk, 
                "id": f'{atricle.source}_{chunk_id}',
                "metadata":{
                "source": atricle.source, 
                "start_char": total,
                "end_char": total+len(chunk)-1,
                "excerpt": chunk[:200]
                }})
            total+=len(chunk)
            
        return result

    def clean_article(self, atricle):
        atricle = atricle.lower()
        atricle = emoji.replace_emoji(atricle, replace="")
        atricle = re.sub(r'[*]', '', atricle )
        atricle = re.sub(r'\s+', ' ', atricle )
        return atricle

    def convert_texts_to_embedding(self, chunks):
        for chunk in chunks: chunk["embedding"] = self.embedding_model.encode(self.clean_article(chunk["content"]),
                                                                            convert_to_numpy=True,
                                                                            show_progress_bar=False)
        return chunks

    def save_embeddings(self, converted_chunks):
        source = converted_chunks[0]["metadata"]["source"]
        self.collection.delete(where={"source": source})
        self.collection.add(
            embeddings=[chunk["embedding"] for chunk in converted_chunks], 
            documents=[chunk["content"] for chunk in converted_chunks],
            metadatas=[chunk["metadata"] for chunk in converted_chunks],
            ids=[chunk["id"] for chunk in converted_chunks]
        )

    def add_one_article(self, article):
        if not(article.content) or not(article.source):
            return None
        chunks = self.split_article(article)
        converted_chunks = self.convert_texts_to_embedding(chunks)
        self.save_embeddings(converted_chunks)
        pass

    def generate_context(self, db_answer):
        if not(db_answer):
            return None
        context = '''
        Here is a list of sources, the higher the source in the list, the more relevant and important it is.\n
        But take into account all the sources.
        '''
        for i in range(len(db_answer["ids"])):
            context += f'\nName of the source: {db_answer["metadatas"][0][i]["source"]}'
            context += f'''\nStart of excerpt: {db_answer["metadatas"][0][i]["start_char"]}
                           \nEnd of excerpt: {db_answer["metadatas"][0][i]["end_char"]}'''
            context += f'\nContent: {db_answer["documents"][0][i]}'

        return context 

    def add_many_articles(self, articles):
        for article in articles: self.add_one_article(article)

    def process_user_issue(self, issue):
        cleaned_text = self.clean_article(issue)
        embedding = self.embedding_model.encode(cleaned_text, convert_to_numpy=True, show_progress_bar=False)
        answer = self.collection.query(query_embeddings=[embedding], n_results=5)
        context =  self.generate_context(answer)
        promt = f''' 
        You are a specialist in bioinformatics and biology. Use only information from the listed sources. 
        If the answer is not found in the sources, say so directly.
        IMPORTANT: DO NOT INVENT ANYTHING BASED ONLY ON FACTS FROM THE SOURCES
        Question: {cleaned_text}
        Context:
        {context}
        Answer format:
        Sources: [list of sources with offsets]
        Short answer.
        Details: <detailed answer with links to sources via [source:start-end]>'''
        answer = self.generate_model.invoke(promt).content
        return answer

