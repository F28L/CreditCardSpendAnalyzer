"""Tests for database models."""
import pytest
from datetime import date, datetime
from models.account import Account
from models.transaction import Transaction
from models.ai_insight import AIInsight
from models.plaid_item import PlaidItem
from sqlalchemy import select


@pytest.mark.asyncio
async def test_create_account(test_session):
    """Test creating an account."""
    account = Account(
        plaid_account_id="test_account_123",
        account_name="Test Credit Card",
        account_type="credit",
        institution_name="Test Bank",
        last_four="1234",
    )
    test_session.add(account)
    await test_session.commit()

    # Query back
    result = await test_session.execute(
        select(Account).where(Account.plaid_account_id == "test_account_123")
    )
    db_account = result.scalar_one()

    assert db_account.account_name == "Test Credit Card"
    assert db_account.account_type == "credit"
    assert db_account.last_four == "1234"


@pytest.mark.asyncio
async def test_create_transaction(test_session):
    """Test creating a transaction."""
    # Create account first
    account = Account(
        plaid_account_id="test_account_123",
        account_name="Test Credit Card",
        account_type="credit",
    )
    test_session.add(account)
    await test_session.commit()

    # Create transaction
    transaction = Transaction(
        external_id="txn_123",
        account_id=account.id,
        amount=50.25,
        date=date(2024, 1, 15),
        merchant_name="Coffee Shop",
        description="Morning coffee",
        category="Food and Drink",
        source="plaid",
        is_reimbursement=False,
    )
    test_session.add(transaction)
    await test_session.commit()

    # Query back
    result = await test_session.execute(
        select(Transaction).where(Transaction.external_id == "txn_123")
    )
    db_transaction = result.scalar_one()

    assert db_transaction.amount == 50.25
    assert db_transaction.merchant_name == "Coffee Shop"
    assert db_transaction.source == "plaid"


@pytest.mark.asyncio
async def test_create_ai_insight(test_session):
    """Test creating an AI insight."""
    insight = AIInsight(
        insight_type="monthly_summary",
        date_range_start=date(2024, 1, 1),
        date_range_end=date(2024, 1, 31),
        content="You spent $1,500 in January on dining out.",
        model_used="llama3",
    )
    test_session.add(insight)
    await test_session.commit()

    # Query back
    result = await test_session.execute(
        select(AIInsight).where(AIInsight.insight_type == "monthly_summary")
    )
    db_insight = result.scalar_one()

    assert db_insight.content == "You spent $1,500 in January on dining out."
    assert db_insight.model_used == "llama3"


@pytest.mark.asyncio
async def test_create_plaid_item(test_session):
    """Test creating a Plaid item."""
    plaid_item = PlaidItem(
        access_token="access-sandbox-token-123",
        item_id="item_123",
        institution_id="ins_123",
    )
    test_session.add(plaid_item)
    await test_session.commit()

    # Query back
    result = await test_session.execute(
        select(PlaidItem).where(PlaidItem.item_id == "item_123")
    )
    db_item = result.scalar_one()

    assert db_item.access_token == "access-sandbox-token-123"
    assert db_item.institution_id == "ins_123"


@pytest.mark.asyncio
async def test_account_transaction_relationship(test_session):
    """Test the relationship between Account and Transaction."""
    # Create account
    account = Account(
        plaid_account_id="test_account_123",
        account_name="Test Credit Card",
        account_type="credit",
    )
    test_session.add(account)
    await test_session.commit()

    # Create multiple transactions
    for i in range(3):
        transaction = Transaction(
            external_id=f"txn_{i}",
            account_id=account.id,
            amount=100.0 + i,
            date=date(2024, 1, i + 1),
            merchant_name=f"Merchant {i}",
            source="plaid",
        )
        test_session.add(transaction)
    await test_session.commit()

    # Query account with transactions
    result = await test_session.execute(
        select(Account).where(Account.id == account.id)
    )
    db_account = result.scalar_one()

    # Check relationship
    assert len(db_account.transactions) == 3
    assert db_account.transactions[0].merchant_name == "Merchant 0"
