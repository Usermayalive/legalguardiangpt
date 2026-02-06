import json
import re
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os

class CUADLoader:
    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2'):
        print(f"Initializing CUADLoader with model: {embedding_model}")
        self.model = SentenceTransformer(embedding_model)
        self.chroma_client = chromadb.PersistentClient(
            path="chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
    def load_and_process_cuad(self, filepath: str = "data/CUAD_v1.json"):
        """Load CUAD dataset and extract legal clauses"""
        print(f"Loading CUAD dataset from: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            print("Falling back to sample clauses...")
            return self._load_sample_clauses()
        
        clauses = []
        
        if 'data' in data:
            print(f"Found {len(data['data'])} documents in CUAD format")
            for document in data['data']:
                title = document.get('title', 'Unknown')
                if 'paragraphs' in document:
                    for paragraph in document['paragraphs']:
                        if 'context' in paragraph:
                            context = paragraph['context']
                            chunks = self._chunk_legal_text(context)
                            
                            for i, chunk in enumerate(chunks):
                                clause_type = self._detect_clause_type(chunk)
                                
                                clauses.append({
                                    'id': f"{title}_{i}",
                                    'text': chunk,
                                    'clause_type': clause_type,
                                    'document_title': title,
                                    'metadata': {
                                        'length': len(chunk),
                                        'chunk_index': i,
                                        'total_chunks': len(chunks)
                                    }
                                })
        else:
            print("Assuming simple clauses format")
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    text = item.get('text', str(item))
                    clause_type = item.get('type', item.get('clause_type', 'General'))
                else:
                    text = str(item)
                    clause_type = 'General'
                
                chunks = self._chunk_legal_text(text)
                for j, chunk in enumerate(chunks):
                    clauses.append({
                        'id': f"clause_{i}_{j}",
                        'text': chunk,
                        'clause_type': clause_type,
                        'document_title': f"Document_{i}",
                        'metadata': {
                            'length': len(chunk),
                            'chunk_index': j,
                            'total_chunks': len(chunks)
                        }
                    })
        
        print(f"Processed {len(clauses)} legal text chunks")
        return clauses
    
    def _load_sample_clauses(self) -> List[Dict]:
        """Load sample clauses if CUAD file is not available"""
        sample_clauses = [
            {
                'id': 'confidentiality_1',
                'text': 'Confidential Information shall mean all information disclosed by one party to the other, whether before or after the Effective Date, that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and the circumstances of disclosure.',
                'clause_type': 'Confidentiality',
                'document_title': 'Sample_NDA'
            },
            {
                'id': 'confidentiality_2',
                'text': 'The Receiving Party agrees to use the Confidential Information only for the Purpose and not to disclose such information to any third party without the prior written consent of the Disclosing Party.',
                'clause_type': 'Confidentiality',
                'document_title': 'Sample_NDA'
            },
            {
                'id': 'termination_1',
                'text': 'This Agreement shall terminate automatically upon the completion of the Services, or may be terminated by either party upon thirty (30) days written notice.',
                'clause_type': 'Termination',
                'document_title': 'Sample_Service_Agreement'
            },
            {
                'id': 'liability_1',
                'text': 'Neither party shall be liable for any indirect, incidental, special, consequential, or punitive damages, including lost profits or revenue.',
                'clause_type': 'Liability',
                'document_title': 'Sample_Agreement'
            },
            {
                'id': 'indemnification_1',
                'text': 'Each party shall indemnify and hold harmless the other party from and against any claims, damages, or losses arising from its breach of this Agreement.',
                'clause_type': 'Indemnification',
                'document_title': 'Sample_Agreement'
            },
            {
                'id': 'governing_law_1',
                'text': 'This Agreement shall be governed by and construed in accordance with the laws of the State of New York, without regard to its conflict of laws principles.',
                'clause_type': 'Governing_Law',
                'document_title': 'Sample_Agreement'
            }
        ]
        
        for clause in sample_clauses:
            clause['metadata'] = {
                'length': len(clause['text']),
                'chunk_index': 0,
                'total_chunks': 1
            }
        
        print(f"Loaded {len(sample_clauses)} sample clauses")
        return sample_clauses
    
    def _detect_clause_type(self, text: str) -> str:
        """Detect the type of legal clause based on keywords"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['confidential', 'nondisclosure', 'proprietary']):
            return 'Confidentiality'
        elif any(word in text_lower for word in ['terminat', 'expir', 'survive']):
            return 'Termination'
        elif any(word in text_lower for word in ['liability', 'liable', 'damage', 'limitation']):
            return 'Liability'
        elif any(word in text_lower for word in ['indemnif', 'hold harmless', 'defend']):
            return 'Indemnification'
        elif any(word in text_lower for word in ['govern', 'jurisdiction', 'law', 'court']):
            return 'Governing_Law'
        elif any(word in text_lower for word in ['intellectual property', 'ip', 'patent', 'copyright']):
            return 'IP'
        elif any(word in text_lower for word in ['warrant', 'represent', 'covenant']):
            return 'Representations'
        else:
            return 'General'
    
    def _chunk_legal_text(self, text: str, max_length: int = 500) -> List[str]:
        """Split legal text into manageable chunks"""
        if len(text) <= max_length:
            return [text]
        
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length > max_length and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def create_embeddings(self, clauses: List[Dict], collection_name: str = "legal_clauses"):
        """Create embeddings and store in ChromaDB"""
        print(f"Creating embeddings for {len(clauses)} clauses...")
        
        try:
            collection = self.chroma_client.get_collection(collection_name)
            print(f"Using existing collection: {collection_name}")
            
            count = collection.count()
            if count > 0:
                print(f"Collection already has {count} embeddings")
                return collection
                
        except Exception as e:
            print(f"Creating new collection: {collection_name}")
            collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "CUAD Legal Clauses", "version": "1.0"}
            )
        
        ids = [c['id'] for c in clauses]
        documents = [c['text'] for c in clauses]
        metadatas = [{
            'clause_type': c['clause_type'],
            'document_title': c['document_title'],
            'length': c['metadata']['length'],
            'source': 'CUAD'
        } for c in clauses]
        
        print("Generating embeddings...")
        embeddings = self.model.encode(documents).tolist()
        
        print("Storing in ChromaDB...")
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Stored {len(clauses)} embeddings in ChromaDB collection: {collection_name}")
        return collection
    
    def search_similar_clauses(self, query: str, n_results: int = 5, min_score: float = 0.3) -> List[Dict]:
        """Search for similar legal clauses"""
        try:
            collection = self.chroma_client.get_collection("legal_clauses")
        except Exception as e:
            print(f"Error getting collection: {e}")
            return []
        
        print(f"Searching for: '{query}'")
        
        query_embedding = self.model.encode([query]).tolist()
        
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        similar_clauses = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                similarity = 1 - results['distances'][0][i]
                if similarity >= min_score:
                    similar_clauses.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': round(similarity, 3)
                    })
        
        print(f"Found {len(similar_clauses)} similar clauses (min score: {min_score})")
        return similar_clauses
    
    def get_collection_info(self):
        """Get information about the collection"""
        try:
            collection = self.chroma_client.get_collection("legal_clauses")
            count = collection.count()
            return {
                "collection_name": "legal_clauses",
                "document_count": count,
                "status": "active"
            }
        except:
            return {
                "collection_name": "legal_clauses",
                "document_count": 0,
                "status": "not found"
            }
