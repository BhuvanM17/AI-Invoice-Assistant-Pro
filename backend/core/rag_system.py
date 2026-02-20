import os
import pickle
import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


@dataclass
class FAQ:
    question: str
    answer: str
    category: str = "general"
    embeddings: List[float] = None


class FAQRAGSystem:
    """
    Retrieval-Augmented Generation system for FAQ retrieval
    Uses TF-IDF for similarity matching and Gemini for context-aware responses
    """

    def __init__(self, model_name="gemini-2.5-flash"):
        self.faqs: List[FAQ] = []
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=10000
        )
        self.faq_vectors = None
        self.model = genai.GenerativeModel(model_name)

        # Load predefined FAQs
        self._load_default_faqs()
        self._build_index()

    def _load_default_faqs(self):
        """Load default FAQs for the e-commerce invoice assistant"""
        default_faqs = [
            FAQ(
                "How do I create an invoice?",
                "You can create an invoice by providing product details like quantity and price. "
                "For example: '2x T-shirts @ 500' creates an invoice with 2 T-shirts at Rs. 500 each.",
                "billing"
            ),
            FAQ(
                "What information do I need for an invoice?",
                "You need at least one product item, customer name, and customer email. "
                "Additional details like GST number, shipping fee, and discount codes can be added.",
                "billing"
            ),
            FAQ(
                "How do I add items to my invoice?",
                "You can add items by mentioning quantity, name, and price. "
                "Examples: '3 shirts @ 499', '1 laptop 12999', '2 books at 299 each'.",
                "billing"
            ),
            FAQ(
                "Can I update my invoice after creation?",
                "Yes, you can continue adding items or updating details in the same conversation. "
                "The system remembers your invoice draft until it's finalized.",
                "billing"
            ),
            FAQ(
                "How do I download my invoice as PDF?",
                "Once your invoice is generated, you'll see a download link in the chat interface. "
                "The PDF is automatically created when your invoice is finalized.",
                "pdf"
            ),
            FAQ(
                "What is GST and how is it calculated?",
                "GST (Goods and Services Tax) is calculated as a percentage of the subtotal. "
                "By default, it's set to 18%, but you can specify a different rate.",
                "tax"
            ),
            FAQ(
                "Can I apply discounts to my invoice?",
                "Yes, you can apply discounts by mentioning a discount code or amount. "
                "Examples: 'Apply 10% discount', 'Use code SAVE10', 'Discount of 500'.",
                "billing"
            ),
            FAQ(
                "How do I include shipping charges?",
                "Shipping charges are automatically added to your invoice. "
                "You can specify shipping fees like: 'Shipping: 100' or 'Delivery charge: 50'.",
                "billing"
            ),
            FAQ(
                "What payment methods do you accept?",
                "This system generates invoices for your records. "
                "Actual payment methods depend on the merchant you're purchasing from.",
                "payment"
            ),
            FAQ(
                "How do I cancel my invoice?",
                "Invoices are generated only when complete. "
                "If you want to start fresh, just begin a new conversation or say 'reset'.",
                "billing"
            ),
            FAQ(
                "Can I send the invoice to someone else?",
                "Yes, once generated, you can download the PDF and share it. "
                "The system also stores invoices by ID for future reference.",
                "pdf"
            ),
            FAQ(
                "How long are my invoices stored?",
                "Invoices are stored in our secure database. "
                "You can retrieve them using the invoice ID provided after generation.",
                "storage"
            )
        ]

        self.faqs = default_faqs

    def add_faq(self, question: str, answer: str, category: str = "general"):
        """Add a new FAQ to the system"""
        faq = FAQ(question=question, answer=answer, category=category)
        self.faqs.append(faq)
        self._build_index()  # Rebuild index after adding new FAQ

    def _build_index(self):
        """Build TF-IDF index for all FAQs"""
        if not self.faqs:
            self.faq_vectors = None
            return

        questions = [faq.question for faq in self.faqs]
        try:
            self.faq_vectors = self.vectorizer.fit_transform(questions)
        except ValueError:
            # Handle case where there are no valid documents
            self.faq_vectors = None

    def _find_similar_faqs(self, query: str, top_k: int = 3) -> List[Tuple[FAQ, float]]:
        """Find top-k similar FAQs based on cosine similarity"""
        if not self.faq_vectors.any() or not query.strip():
            return []

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(
            query_vector, self.faq_vectors).flatten()

        # Get indices of top-k similar FAQs
        top_indices = similarities.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Only return if similarity is above threshold
                results.append((self.faqs[idx], similarities[idx]))

        return results

    def get_answer(self, query: str) -> Tuple[str, bool]:
        """
        Get answer from RAG system

        Returns:
            Tuple[str, bool]: (answer, is_from_faq)
        """
        # First, try to find similar FAQs
        similar_faqs = self._find_similar_faqs(query, top_k=2)

        if similar_faqs and similar_faqs[0][1] > 0.3:  # High confidence match
            best_match, confidence = similar_faqs[0]
            return best_match.answer, True

        # If no good match found, return None to indicate RAG didn't have answer
        return None, False

    def get_contextual_answer(self, query: str, conversation_context: str = "") -> str:
        """
        Get a contextual answer using Gemini with FAQ context
        """
        # Try to find relevant FAQs first
        faq_answer, is_from_faq = self.get_answer(query)

        if is_from_faq:
            # Use LLM to generate a contextual response based on the FAQ answer
            context_prompt = f"""
            You are an AI assistant for an e-commerce invoice system. 
            Based on the user's query and the FAQ answer below, provide a helpful response.
            
            User Query: {query}
            
            FAQ Answer: {faq_answer}
            
            Conversation Context: {conversation_context}
            
            Provide a helpful, concise response that addresses the user's specific query.
            If the FAQ doesn't fully address the query, acknowledge the limitation and offer assistance.
            """

            try:
                response = self.model.generate_content(context_prompt)
                return response.text
            except Exception:
                # Fallback to direct FAQ answer
                return faq_answer
        else:
            # No relevant FAQ found, return None to indicate use general LLM
            return None

    def search_faqs_by_category(self, category: str) -> List[FAQ]:
        """Search FAQs by category"""
        return [faq for faq in self.faqs if faq.category.lower() == category.lower()]

    def get_all_categories(self) -> List[str]:
        """Get all available FAQ categories"""
        return list(set(faq.category for faq in self.faqs))


# Global instance
rag_system = FAQRAGSystem()


def get_faq_answer(query: str, conversation_context: str = "") -> str:
    """
    Convenience function to get FAQ answer
    """
    return rag_system.get_contextual_answer(query, conversation_context)


if __name__ == "__main__":
    # Test the RAG system
    test_queries = [
        "How do I create an invoice?",
        "What information do I need?",
        "How to add items?",
        "Payment methods"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        answer = get_faq_answer(query)
        if answer:
            print(f"Answer: {answer}")
        else:
            print("No relevant FAQ found.")
        print("-" * 50)
