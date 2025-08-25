"""
Enhanced utilities for document analysis and insights
"""
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import re
from datetime import datetime

from ..models import Document, DocumentChunk


class DocumentAnalyzer:
    """Advanced document analysis and insights"""
    
    def __init__(self):
        self.stop_words = {
            'el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le',
            'da', 'su', 'por', 'son', 'con', 'para', 'del', 'las', 'al', 'una', 'sus',
            'ser', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando',
            'todo', 'esta', 'tras', 'otros', 'hasta', 'hay', 'donde', 'quien', 'desde',
            'todos', 'durante', 'todos', 'uno', 'muy', 'era', 'años', 'hasta', 'debe',
            'pueden', 'cada', 'fue', 'ser', 'han', 'más', 'pero', 'como', 'así', 'mismo'
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {
            'dates': [],
            'numbers': [],
            'emails': [],
            'urls': [],
            'capitalized_words': []
        }
        
        # Extract dates (simple patterns)
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2} de \w+ de \d{4}'
        ]
        
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text))
        
        # Extract numbers
        entities['numbers'] = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        
        # Extract emails
        entities['emails'] = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        # Extract URLs
        entities['urls'] = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        # Extract capitalized words (potential proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
        entities['capitalized_words'] = list(set(capitalized))
        
        return entities
    
    def calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not sentences or not words:
            return {'flesch_reading_ease': 0, 'avg_sentence_length': 0, 'avg_word_length': 0}
        
        # Basic metrics
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simplified Flesch Reading Ease (approximation)
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
        flesch_score = max(0, min(100, flesch_score))
        
        return {
            'flesch_reading_ease': round(flesch_score, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(avg_word_length, 2),
            'total_sentences': len(sentences),
            'total_words': len(words)
        }
    
    def find_similarities(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Find similarities between documents"""
        if len(documents) < 2:
            return []
        
        similarities = []
        
        for i, doc1 in enumerate(documents):
            for j, doc2 in enumerate(documents[i+1:], i+1):
                # Calculate word overlap
                words1 = set(re.findall(r'\b\w+\b', doc1.content.lower())) if doc1.content else set()
                words2 = set(re.findall(r'\b\w+\b', doc2.content.lower())) if doc2.content else set()
                
                # Remove stop words
                words1 = words1 - self.stop_words
                words2 = words2 - self.stop_words
                
                if words1 and words2:
                    common_words = words1.intersection(words2)
                    similarity_score = len(common_words) / len(words1.union(words2))
                    
                    similarities.append({
                        'doc1': doc1.filename,
                        'doc2': doc2.filename,
                        'similarity_score': round(similarity_score, 3),
                        'common_words': list(common_words)[:10],  # Top 10 common words
                        'total_common': len(common_words)
                    })
        
        return sorted(similarities, key=lambda x: x['similarity_score'], reverse=True)
    
    def generate_document_summary(self, document: Document) -> Dict[str, Any]:
        """Generate comprehensive document summary"""
        if not document.content:
            return {'error': 'No content available'}
        
        # Basic statistics
        words = re.findall(r'\b\w+\b', document.content.lower())
        sentences = re.split(r'[.!?]+', document.content)
        paragraphs = document.content.split('\n\n')
        
        # Readability
        readability = self.calculate_readability(document.content)
        
        # Entities
        entities = self.extract_entities(document.content)
        
        # Most frequent words (excluding stop words)
        word_freq = Counter(word for word in words if word not in self.stop_words and len(word) > 2)
        
        return {
            'basic_stats': {
                'characters': len(document.content),
                'words': len(words),
                'sentences': len([s for s in sentences if s.strip()]),
                'paragraphs': len([p for p in paragraphs if p.strip()])
            },
            'readability': readability,
            'entities': entities,
            'top_words': dict(word_freq.most_common(20)),
            'topics': document.topics[:10] if document.topics else [],
            'estimated_reading_time': round(len(words) / 200, 1)  # ~200 words per minute
        }
    
    def compare_documents_detailed(self, documents: List[Document]) -> Dict[str, Any]:
        """Detailed comparison between documents"""
        if len(documents) < 2:
            return {'error': 'At least 2 documents needed for comparison'}
        
        comparison = {
            'document_count': len(documents),
            'individual_summaries': {},
            'similarities': self.find_similarities(documents),
            'overall_stats': {
                'total_words': 0,
                'total_characters': 0,
                'avg_readability': 0
            },
            'common_themes': [],
            'unique_themes': {}
        }
        
        all_topics = []
        readability_scores = []
        
        # Analyze each document
        for doc in documents:
            summary = self.generate_document_summary(doc)
            comparison['individual_summaries'][doc.filename] = summary
            
            # Aggregate stats
            comparison['overall_stats']['total_words'] += summary['basic_stats']['words']
            comparison['overall_stats']['total_characters'] += summary['basic_stats']['characters']
            
            if 'flesch_reading_ease' in summary['readability']:
                readability_scores.append(summary['readability']['flesch_reading_ease'])
            
            # Collect topics
            if doc.topics:
                all_topics.extend(doc.topics)
        
        # Calculate averages
        if readability_scores:
            comparison['overall_stats']['avg_readability'] = round(
                sum(readability_scores) / len(readability_scores), 2
            )
        
        # Find common themes
        topic_counter = Counter(all_topics)
        common_threshold = max(2, len(documents) // 2)
        comparison['common_themes'] = [
            topic for topic, count in topic_counter.items() 
            if count >= common_threshold
        ]
        
        # Find unique themes per document
        for doc in documents:
            if doc.topics:
                unique = [topic for topic in doc.topics if topic_counter[topic] == 1]
                if unique:
                    comparison['unique_themes'][doc.filename] = unique[:5]
        
        return comparison


class InsightGenerator:
    """Generate insights and recommendations from document analysis"""
    
    def __init__(self):
        self.analyzer = DocumentAnalyzer()
    
    def generate_insights(self, documents: List[Document]) -> Dict[str, Any]:
        """Generate comprehensive insights from documents"""
        if not documents:
            return {'error': 'No documents provided'}
        
        # Get detailed comparison
        comparison = self.analyzer.compare_documents_detailed(documents)
        
        insights = {
            'document_overview': {
                'total_documents': len(documents),
                'total_size_mb': sum(doc.size_bytes for doc in documents) / (1024 * 1024),
                'file_types': list(set(doc.file_type.value for doc in documents))
            },
            'content_insights': [],
            'recommendations': [],
            'quality_assessment': {},
            'processing_suggestions': []
        }
        
        # Content insights
        if comparison['overall_stats']['total_words'] > 10000:
            insights['content_insights'].append(
                "📚 Corpus extenso detectado - ideal para análisis profundo"
            )
        
        if len(comparison['common_themes']) > 5:
            insights['content_insights'].append(
                f"🔗 Alta cohesión temática - {len(comparison['common_themes'])} temas comunes identificados"
            )
        
        # Quality assessment
        avg_readability = comparison['overall_stats'].get('avg_readability', 0)
        if avg_readability > 60:
            insights['quality_assessment']['readability'] = "✅ Fácil lectura"
        elif avg_readability > 30:
            insights['quality_assessment']['readability'] = "⚠️ Lectura moderada"
        else:
            insights['quality_assessment']['readability'] = "❌ Lectura difícil"
        
        # Recommendations
        if len(documents) > 2:
            insights['recommendations'].append(
                "💡 Considera usar preguntas de comparación entre documentos"
            )
        
        if comparison['overall_stats']['total_words'] > 5000:
            insights['recommendations'].append(
                "🎯 Usa preguntas específicas para obtener mejores resultados"
            )
        
        # Processing suggestions
        insights['processing_suggestions'] = [
            "📊 Solicita resúmenes por tema específico",
            "🔍 Haz preguntas sobre datos específicos (fechas, números, nombres)",
            "⚖️ Compara perspectivas entre documentos",
            "📈 Pide análisis de tendencias o patrones"
        ]
        
        return insights
