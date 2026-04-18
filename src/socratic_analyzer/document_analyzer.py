"""Document analysis for semantic understanding and extraction."""
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class Document:
    content: str
    doc_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.doc_id:
            self.doc_id = hashlib.md5(self.content.encode()).hexdigest()[:12]

@dataclass
class DocumentAnalysisResult:
    document_id: str
    content_summary: str
    key_concepts: List[str]
    semantic_score: float
    text_complexity: float
    readability_level: str
    entities: List[str]
    sentiment: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "content_summary": self.content_summary,
            "key_concepts": self.key_concepts,
            "semantic_score": self.semantic_score,
            "text_complexity": self.text_complexity,
            "readability_level": self.readability_level,
            "entities": self.entities,
            "sentiment": self.sentiment,
        }

class DocumentAnalyzer:
    """Analyzes documents for semantic understanding."""

    def __init__(self):
        self.documents = {}
        self.analysis_cache = {}

    def analyze(self, doc: Document) -> DocumentAnalysisResult:
        """Analyze a document."""
        if doc.doc_id in self.analysis_cache:
            return self.analysis_cache[doc.doc_id]

        # Extract basic features
        content = doc.content
        words = content.split()
        sentences = content.split('.')

        # Simple heuristics
        key_concepts = self._extract_concepts(content)
        complexity = len(words) / max(len(sentences), 1) / 15.0
        complexity = min(1.0, complexity)

        # Readability heuristic (Flesch Kincaid approximation)
        if complexity < 0.3:
            readability = "Very Easy"
        elif complexity < 0.5:
            readability = "Easy"
        elif complexity < 0.7:
            readability = "Intermediate"
        elif complexity < 0.85:
            readability = "Advanced"
        else:
            readability = "Expert"

        result = DocumentAnalysisResult(
            document_id=doc.doc_id,
            content_summary=self._summarize(content),
            key_concepts=key_concepts,
            semantic_score=0.85,
            text_complexity=complexity,
            readability_level=readability,
            entities=self._extract_entities(content),
            sentiment=self._analyze_sentiment(content),
        )

        self.analysis_cache[doc.doc_id] = result
        self.documents[doc.doc_id] = doc
        return result

    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text."""
        # Simple keyword extraction
        words = text.lower().split()
        # Filter common words and return unique concepts
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'to', 'of', 'in', 'at'}
        concepts = list(set([w for w in words if w not in common_words and len(w) > 3]))
        return concepts[:5]  # Top 5 concepts

    def _summarize(self, text: str) -> str:
        """Create a text summary."""
        sentences = text.split('.')
        if len(sentences) <= 2:
            return text
        return '. '.join(sentences[:2]) + '.'

    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities (simple heuristic)."""
        # Very simple: look for capitalized words
        words = text.split()
        entities = [w for w in words if w and w[0].isupper() and len(w) > 3]
        return list(set(entities))[:5]

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text."""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'positive'}
        negative_words = {'bad', 'poor', 'terrible', 'awful', 'negative', 'worst'}

        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

class AdaptiveDocumentLoader:
    """Intelligently loads and processes documents based on analysis."""

    def __init__(self, analyzer: Optional[DocumentAnalyzer] = None):
        self.analyzer = analyzer or DocumentAnalyzer()
        self.loaded_documents = {}
        self.loading_strategies = {}

    def load_document(self, content: str, metadata: Optional[Dict] = None) -> Document:
        """Load and process a document adaptively."""
        doc = Document(content=content, metadata=metadata or {})
        analysis = self.analyzer.analyze(doc)

        # Adapt processing based on complexity
        if analysis.text_complexity > 0.7:
            strategy = "chunked"  # Break into chunks
            chunk_size = max(500, int(5000 * (1 - analysis.text_complexity)))
        else:
            strategy = "full"
            chunk_size = len(content)

        self.loading_strategies[doc.doc_id] = {
            "strategy": strategy,
            "chunk_size": chunk_size,
            "analysis": analysis.to_dict(),
        }

        self.loaded_documents[doc.doc_id] = doc
        return doc

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a loaded document."""
        return self.loaded_documents.get(doc_id)

    def get_strategy(self, doc_id: str) -> Dict[str, Any]:
        """Get loading strategy for a document."""
        return self.loading_strategies.get(doc_id, {})

    def adaptive_chunk(self, doc_id: str) -> List[str]:
        """Split document into chunks based on adaptive strategy."""
        doc = self.loaded_documents.get(doc_id)
        if not doc:
            return []

        strategy = self.loading_strategies.get(doc_id, {})
        chunk_size = strategy.get("chunk_size", len(doc.content))

        chunks = []
        for i in range(0, len(doc.content), chunk_size):
            chunks.append(doc.content[i:i+chunk_size])

        return chunks
