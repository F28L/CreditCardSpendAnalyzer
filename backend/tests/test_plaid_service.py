"""Tests for Plaid service."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from services.plaid_service import PlaidService


@pytest.mark.asyncio
async def test_create_link_token():
    """Test creating a Plaid link token."""
    with patch("services.plaid_service.plaid_api.PlaidApi") as MockPlaidApi:
        mock_client = MockPlaidApi.return_value
        mock_client.link_token_create.return_value = {"link_token": "link-test-token"}

        service = PlaidService()
        link_token = await service.create_link_token(user_id="test-user")

        assert link_token == "link-test-token"
        mock_client.link_token_create.assert_called_once()


@pytest.mark.asyncio
async def test_exchange_public_token():
    """Test exchanging public token for access token."""
    with patch("services.plaid_service.plaid_api.PlaidApi") as MockPlaidApi:
        mock_client = MockPlaidApi.return_value
        mock_client.item_public_token_exchange.return_value = {
            "access_token": "access-test-token",
            "item_id": "item-123",
        }

        service = PlaidService()
        access_token, item_id = await service.exchange_public_token("public-token")

        assert access_token == "access-test-token"
        assert item_id == "item-123"


@pytest.mark.asyncio
async def test_get_accounts():
    """Test getting accounts from Plaid."""
    with patch("services.plaid_service.plaid_api.PlaidApi") as MockPlaidApi:
        mock_client = MockPlaidApi.return_value
        mock_client.accounts_get.return_value = {
            "accounts": [
                {
                    "account_id": "acc-123",
                    "name": "Chase Credit Card",
                    "type": "credit",
                    "subtype": "credit card",
                    "mask": "1234",
                    "official_name": "Chase Freedom",
                }
            ]
        }

        service = PlaidService()
        accounts = await service.get_accounts("access-token")

        assert len(accounts) == 1
        assert accounts[0]["plaid_account_id"] == "acc-123"
        assert accounts[0]["account_name"] == "Chase Credit Card"
        assert accounts[0]["account_type"] == "credit"


@pytest.mark.asyncio
async def test_sync_transactions_pagination():
    """Test syncing transactions with pagination."""
    with patch("services.plaid_service.plaid_api.PlaidApi") as MockPlaidApi:
        mock_client = MockPlaidApi.return_value

        # Simulate pagination: first call returns 500 transactions, second returns 250
        mock_client.transactions_get.side_effect = [
            {
                "transactions": [
                    {
                        "transaction_id": f"txn-{i}",
                        "account_id": "acc-123",
                        "amount": 50.0 + i,
                        "date": "2024-01-15",
                        "merchant_name": f"Merchant {i}",
                        "name": f"Purchase {i}",
                        "category": ["Food and Drink"],
                        "pending": False,
                    }
                    for i in range(500)
                ],
                "total_transactions": 750,
            },
            {
                "transactions": [
                    {
                        "transaction_id": f"txn-{i}",
                        "account_id": "acc-123",
                        "amount": 50.0 + i,
                        "date": "2024-01-16",
                        "merchant_name": f"Merchant {i}",
                        "name": f"Purchase {i}",
                        "category": ["Food and Drink"],
                        "pending": False,
                    }
                    for i in range(500, 750)
                ],
                "total_transactions": 750,
            },
        ]

        service = PlaidService()
        transactions = await service.sync_transactions(
            "access-token",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
        )

        assert len(transactions) == 750
        assert mock_client.transactions_get.call_count == 2


@pytest.mark.asyncio
async def test_sync_transactions_default_24_months():
    """Test that sync defaults to 24 months if no dates provided."""
    with patch("services.plaid_service.plaid_api.PlaidApi") as MockPlaidApi:
        mock_client = MockPlaidApi.return_value
        mock_client.transactions_get.return_value = {
            "transactions": [],
            "total_transactions": 0,
        }

        service = PlaidService()
        transactions = await service.sync_transactions("access-token")

        # Check that transactions_get was called
        assert mock_client.transactions_get.called

        # Get the actual call arguments
        call_args = mock_client.transactions_get.call_args[0][0]

        # Verify date range is approximately 24 months
        start_date = call_args.start_date
        end_date = call_args.end_date

        # Calculate difference (should be around 730 days / 24 months)
        date_diff = (end_date - start_date).days
        assert 720 <= date_diff <= 740  # Allow small variance


@pytest.mark.asyncio
async def test_sync_transactions_with_account_filter():
    """Test syncing transactions for specific accounts."""
    with patch("services.plaid_service.plaid_api.PlaidApi") as MockPlaidApi:
        mock_client = MockPlaidApi.return_value
        mock_client.transactions_get.return_value = {
            "transactions": [
                {
                    "transaction_id": "txn-1",
                    "account_id": "acc-123",
                    "amount": 50.0,
                    "date": "2024-01-15",
                    "merchant_name": "Merchant 1",
                    "name": "Purchase",
                    "category": ["Shopping"],
                    "pending": False,
                }
            ],
            "total_transactions": 1,
        }

        service = PlaidService()
        transactions = await service.sync_transactions(
            "access-token",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            account_ids=["acc-123"],
        )

        assert len(transactions) == 1
        assert transactions[0]["plaid_account_id"] == "acc-123"

        # Verify account_ids filter was passed
        call_args = mock_client.transactions_get.call_args[0][0]
        assert hasattr(call_args.options, "account_ids")
