"""Base LLM provider interface."""
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_insight(self, prompt: str, transactions: List[Dict]) -> str:
        """
        Generate AI insight from transactions.

        Args:
            prompt: The prompt template for the LLM
            transactions: List of transaction dictionaries

        Returns:
            Generated insight text
        """
        pass

    @abstractmethod
    async def categorize_transaction(self, transaction: Dict) -> str:
        """
        Categorize a single transaction using AI.

        Args:
            transaction: Transaction dictionary with keys like merchant_name, amount, description

        Returns:
            Category name
        """
        pass

    @abstractmethod
    async def detect_reimbursement(self, transaction: Dict) -> tuple[bool, float]:
        """
        Detect if a transaction is a reimbursement.

        Args:
            transaction: Transaction dictionary

        Returns:
            Tuple of (is_reimbursement, confidence_score)
        """
        pass
