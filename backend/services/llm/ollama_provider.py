"""Ollama LLM provider implementation."""
import ollama
import json
from typing import List, Dict
from .base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local LLM inference."""

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama provider.

        Args:
            model: Model name (e.g., 'llama3', 'mistral')
            base_url: Ollama API base URL
        """
        self.model = model
        self.base_url = base_url

    async def generate_insight(self, prompt: str, transactions: List[Dict]) -> str:
        """Generate AI insight from transactions using Ollama."""
        # Format transactions for LLM
        tx_text = "\n".join(
            [
                f"- {t.get('date')}: {t.get('merchant_name', 'Unknown')} (${t.get('amount', 0):.2f})"
                for t in transactions
            ]
        )

        full_prompt = f"""{prompt}

Transactions:
{tx_text}

Provide a concise analysis in 3-4 sentences."""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst AI assistant. Provide clear, actionable insights.",
                    },
                    {"role": "user", "content": full_prompt},
                ],
            )
            return response["message"]["content"]
        except Exception as e:
            return f"Error generating insight: {str(e)}"

    async def categorize_transaction(self, transaction: Dict) -> str:
        """Categorize a transaction using Ollama."""
        prompt = f"""Categorize this transaction into ONE of these categories:
Groceries, Dining Out, Transportation, Entertainment, Shopping,
Bills & Utilities, Healthcare, Travel, Personal Care, Other

Transaction: {transaction.get('merchant_name', 'Unknown')} - ${transaction.get('amount', 0):.2f}
Description: {transaction.get('description', 'N/A')}

Respond with ONLY the category name, nothing else."""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            category = response["message"]["content"].strip()
            return category
        except Exception as e:
            return "Other"

    async def detect_reimbursement(self, transaction: Dict) -> tuple[bool, float]:
        """Detect if a transaction is a reimbursement using Ollama."""
        description = transaction.get("description", "")
        merchant = transaction.get("merchant_name", "")

        prompt = f"""Analyze if this transaction is a reimbursement or payment received from someone.

Transaction: {merchant}
Description: {description}
Amount: ${transaction.get('amount', 0):.2f}

Look for keywords like: reimburse, paid back, split, venmo, zelle, repay, refund

Respond in JSON format:
{{"is_reimbursement": true/false, "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            result = json.loads(response["message"]["content"])
            return (result.get("is_reimbursement", False), result.get("confidence", 0.5))
        except Exception:
            # Fallback to keyword detection
            keywords = [
                "reimburse",
                "paid back",
                "split",
                "venmo",
                "zelle",
                "repay",
                "refund",
            ]
            text = f"{description} {merchant}".lower()
            for keyword in keywords:
                if keyword in text:
                    return (True, 0.7)
            return (False, 0.3)
