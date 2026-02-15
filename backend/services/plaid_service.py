"""Plaid API service for financial data integration."""
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid import ApiClient, Configuration
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


class PlaidService:
    """Service for interacting with Plaid API."""

    def __init__(self):
        """Initialize Plaid service with configuration."""
        configuration = Configuration(
            host=self._get_plaid_host(),
            api_key={
                "clientId": settings.PLAID_CLIENT_ID,
                "secret": settings.PLAID_SECRET,
            },
        )
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def _get_plaid_host(self) -> str:
        """Get Plaid API host based on environment."""
        env_map = {
            "sandbox": "https://sandbox.plaid.com",
            "development": "https://development.plaid.com",
            "production": "https://production.plaid.com",
        }
        return env_map.get(settings.PLAID_ENV, "https://sandbox.plaid.com")

    async def create_link_token(self, user_id: str = "user-1") -> str:
        """
        Create a Link token for Plaid Link initialization.

        Args:
            user_id: Unique user identifier

        Returns:
            Link token string
        """
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
                client_name="Finance AI App",
                products=[Products("transactions")],
                country_codes=[CountryCode("US")],
                language="en",
            )
            response = self.client.link_token_create(request)
            return response["link_token"]
        except Exception as e:
            logger.error(f"Error creating link token: {e}")
            raise

    async def exchange_public_token(self, public_token: str) -> tuple[str, str]:
        """
        Exchange a public token for an access token.

        Args:
            public_token: Public token from Plaid Link

        Returns:
            Tuple of (access_token, item_id)
        """
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            return (response["access_token"], response["item_id"])
        except Exception as e:
            logger.error(f"Error exchanging public token: {e}")
            raise

    async def get_accounts(self, access_token: str) -> List[Dict]:
        """
        Get accounts for an access token.

        Args:
            access_token: Plaid access token

        Returns:
            List of account dictionaries
        """
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)

            accounts = []
            for account in response["accounts"]:
                # Convert account type enum to string
                account_type = account["type"]
                if hasattr(account_type, 'value'):
                    account_type = account_type.value
                else:
                    account_type = str(account_type)

                accounts.append({
                    "plaid_account_id": account["account_id"],
                    "account_name": account["name"],
                    "account_type": account_type,
                    "account_subtype": account.get("subtype"),
                    "mask": account.get("mask"),
                    "official_name": account.get("official_name"),
                })

            return accounts
        except Exception as e:
            logger.error(f"Error getting accounts: {e}")
            raise

    async def sync_transactions(
        self,
        access_token: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        account_ids: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Sync transactions from Plaid with pagination support.
        Defaults to last 24 months if no date range specified.

        Args:
            access_token: Plaid access token
            start_date: Start date for transactions (defaults to 24 months ago)
            end_date: End date for transactions (defaults to today)
            account_ids: Optional list of specific account IDs to sync

        Returns:
            List of transaction dictionaries
        """
        # Default to 24 months if not specified
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=730)  # 24 months

        all_transactions = []
        offset = 0
        batch_size = 500  # Plaid max per request
        has_more = True

        logger.info(
            f"Starting transaction sync from {start_date.date()} to {end_date.date()}"
        )

        try:
            while has_more:
                request_options = TransactionsGetRequestOptions(
                    count=batch_size,
                    offset=offset,
                )

                if account_ids:
                    request_options.account_ids = account_ids

                request = TransactionsGetRequest(
                    access_token=access_token,
                    start_date=start_date.date(),
                    end_date=end_date.date(),
                    options=request_options,
                )

                response = self.client.transactions_get(request)
                transactions = response["transactions"]
                total_transactions = response["total_transactions"]

                logger.info(
                    f"Fetched {len(transactions)} transactions (offset: {offset}, total: {total_transactions})"
                )

                # Process transactions
                for txn in transactions:
                    all_transactions.append({
                        "external_id": txn["transaction_id"],
                        "plaid_account_id": txn["account_id"],
                        "amount": float(txn["amount"]),
                        "date": txn["date"],
                        "merchant_name": txn.get("merchant_name") or txn.get("name"),
                        "description": txn.get("name"),
                        "category": (
                            txn["category"][0] if txn.get("category") else None
                        ),
                        "pending": txn.get("pending", False),
                    })

                # Check if there are more transactions
                offset += len(transactions)
                has_more = offset < total_transactions

            logger.info(f"Completed sync: {len(all_transactions)} transactions total")
            return all_transactions

        except Exception as e:
            logger.error(f"Error syncing transactions: {e}")
            raise

    async def get_institution_name(self, access_token: str) -> str:
        """
        Get institution name for an access token.

        Args:
            access_token: Plaid access token

        Returns:
            Institution name
        """
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            # The institution name is typically in the item metadata
            return response.get("item", {}).get("institution_id", "Unknown")
        except Exception as e:
            logger.error(f"Error getting institution: {e}")
            return "Unknown"
