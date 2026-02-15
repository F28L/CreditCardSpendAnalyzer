"""OpenAI LLM provider implementation."""
from openai import AsyncOpenAI
import json
from typing import List, Dict
from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider for cloud-based LLM inference."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (e.g., 'gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4-turbo')
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_insight(self, prompt: str, transactions: List[Dict]) -> str:
        """Generate AI insight from transactions using OpenAI."""
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
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst AI assistant. Provide clear, actionable insights.",
                    },
                    {"role": "user", "content": full_prompt},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating insight: {str(e)}"

    async def categorize_transaction(self, transaction: Dict) -> str:
        """Categorize a transaction using OpenAI."""
        prompt = f"""Categorize this transaction into ONE of these categories:
Groceries, Dining Out, Transportation, Entertainment, Shopping,
Bills & Utilities, Healthcare, Travel, Personal Care, Other

Transaction: {transaction.get('merchant_name', 'Unknown')} - ${transaction.get('amount', 0):.2f}
Description: {transaction.get('description', 'N/A')}

Respond with ONLY the category name, nothing else."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20,
            )
            category = response.choices[0].message.content.strip()
            return category
        except Exception as e:
            return "Other"

    async def detect_reimbursement(self, transaction: Dict) -> tuple[bool, float]:
        """Detect if a transaction is a reimbursement using OpenAI."""
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
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150,
            )
            result = json.loads(response.choices[0].message.content)
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
