"""Seed RAG collections with initial example data."""

import asyncio
import json
from datetime import datetime, timedelta

from test_data_agent.clients.weaviate_client import WeaviateClient
from test_data_agent.clients.weaviate_schema import ensure_collections
from test_data_agent.config import Settings
from test_data_agent.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


# Example test data patterns
TEST_DATA_PATTERNS = [
    {
        "domain": "ecommerce",
        "entity": "cart",
        "scenario": "fitness_shopping",
        "data": json.dumps({
            "cart_id": "CRT-2025-1234567",
            "customer_id": "USR-9876543",
            "items": [
                {"sku": "FIT-RUN-001", "name": "Running Shoes", "quantity": 1, "price": 129.99},
                {"sku": "FIT-SOC-002", "name": "Athletic Socks", "quantity": 3, "price": 12.99},
                {"sku": "FIT-BOT-003", "name": "Water Bottle", "quantity": 1, "price": 24.99},
            ],
            "subtotal": 183.96,
            "tax": 14.72,
            "total": 198.68,
            "created_at": "2025-01-15T10:30:00",
        }),
        "quality_score": 0.95,
        "usage_count": 0,
        "created_at": datetime.now(),
    },
    {
        "domain": "ecommerce",
        "entity": "cart",
        "scenario": "beauty_shopping",
        "data": json.dumps({
            "cart_id": "CRT-2025-2345678",
            "customer_id": "USR-1122334",
            "items": [
                {"sku": "BEA-LIP-001", "name": "Lipstick", "quantity": 2, "price": 22.00},
                {"sku": "BEA-MAS-002", "name": "Mascara", "quantity": 1, "price": 28.00},
                {"sku": "BEA-FOU-003", "name": "Foundation", "quantity": 1, "price": 42.00},
            ],
            "subtotal": 92.00,
            "tax": 7.36,
            "total": 99.36,
            "created_at": "2025-01-16T14:20:00",
        }),
        "quality_score": 0.92,
        "usage_count": 0,
        "created_at": datetime.now(),
    },
    {
        "domain": "ecommerce",
        "entity": "order",
        "scenario": "standard_order",
        "data": json.dumps({
            "order_id": "ORD-2025-3456789",
            "customer_id": "USR-5544332",
            "status": "shipped",
            "items": [
                {"sku": "APP-TEE-001", "name": "T-Shirt", "quantity": 2, "price": 19.99},
                {"sku": "APP-JEA-002", "name": "Jeans", "quantity": 1, "price": 59.99},
            ],
            "subtotal": 99.97,
            "tax": 8.00,
            "shipping_cost": 5.99,
            "total": 113.96,
            "created_at": "2025-01-10T09:15:00",
            "shipped_at": "2025-01-11T16:30:00",
        }),
        "quality_score": 0.90,
        "usage_count": 0,
        "created_at": datetime.now(),
    },
    {
        "domain": "ecommerce",
        "entity": "user",
        "scenario": "platinum_member",
        "data": json.dumps({
            "user_id": "USR-7788990",
            "email": "sarah.johnson@example.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "phone": "(555) 234-5678",
            "loyalty_tier": "platinum",
            "created_at": "2023-03-15T10:00:00",
            "last_login": "2025-01-16T08:45:00",
        }),
        "quality_score": 0.88,
        "usage_count": 0,
        "created_at": datetime.now(),
    },
    {
        "domain": "ecommerce",
        "entity": "review",
        "scenario": "positive_review",
        "data": json.dumps({
            "review_id": "REV-1234567890",
            "product_id": "PROD-123456",
            "user_id": "USR-9988776",
            "rating": 5,
            "title": "Excellent quality, highly recommend!",
            "body": "This product exceeded my expectations. Great quality, fast shipping, and exactly as described. Would definitely purchase again!",
            "verified_purchase": True,
            "helpful_votes": 15,
            "created_at": "2025-01-14T19:30:00",
        }),
        "quality_score": 0.93,
        "usage_count": 0,
        "created_at": datetime.now(),
    },
]

# Example defect patterns
DEFECT_PATTERNS = [
    {
        "defect_id": "BUG-2024-001",
        "domain": "ecommerce",
        "entity": "cart",
        "trigger_data": json.dumps({
            "cart_id": "CRT-2024-0000000",
            "customer_id": "USR-0000000",
            "items": [],  # Empty cart caused null pointer exception
            "subtotal": 0.00,
            "tax": 0.00,
            "total": 0.00,
        }),
        "defect_description": "Empty cart array caused null pointer exception in checkout flow",
        "severity": "high",
        "discovered_at": datetime.now() - timedelta(days=90),
    },
    {
        "defect_id": "BUG-2024-002",
        "domain": "ecommerce",
        "entity": "payment",
        "trigger_data": json.dumps({
            "payment_id": "PAY-2024-1111111",
            "amount": 0.001,  # Decimal precision issue
            "currency": "USD",
            "status": "completed",
        }),
        "defect_description": "Very small decimal amounts (< 0.01) caused rounding errors in payment processing",
        "severity": "medium",
        "discovered_at": datetime.now() - timedelta(days=60),
    },
    {
        "defect_id": "BUG-2024-003",
        "domain": "ecommerce",
        "entity": "user",
        "trigger_data": json.dumps({
            "user_id": "USR-2222222",
            "email": "test+special@example.com",  # Plus sign in email
            "first_name": "José",  # Unicode character
            "last_name": "O'Brien",  # Apostrophe
        }),
        "defect_description": "Special characters in email and name fields caused validation failures",
        "severity": "medium",
        "discovered_at": datetime.now() - timedelta(days=45),
    },
    {
        "defect_id": "BUG-2024-004",
        "domain": "ecommerce",
        "entity": "order",
        "trigger_data": json.dumps({
            "order_id": "ORD-2024-3333333",
            "created_at": "2024-12-31T23:59:59Z",  # Midnight UTC on year boundary
            "updated_at": "2025-01-01T00:00:01Z",
            "status": "pending",
        }),
        "defect_description": "Timezone edge case at year boundary caused date comparison failures",
        "severity": "low",
        "discovered_at": datetime.now() - timedelta(days=30),
    },
    {
        "defect_id": "BUG-2024-005",
        "domain": "ecommerce",
        "entity": "cart",
        "trigger_data": json.dumps({
            "cart_id": "CRT-2024-4444444",
            "items": [
                {"sku": "TST-001", "name": "'; DROP TABLE carts; --", "quantity": 1, "price": 10.00},
            ],
            "subtotal": 10.00,
        }),
        "defect_description": "SQL injection pattern in product name field was not properly sanitized",
        "severity": "critical",
        "discovered_at": datetime.now() - timedelta(days=120),
    },
]

# Example production samples (anonymized)
PRODUCTION_SAMPLES = [
    {
        "domain": "ecommerce",
        "entity": "cart",
        "anonymized_data": json.dumps({
            "cart_id": "CRT-ANON-001",
            "item_count": 3,
            "avg_item_price": 45.67,
            "total_range": "100-200",
            "categories": ["apparel", "accessories"],
        }),
        "distribution_stats": json.dumps({
            "avg_items_per_cart": 3.2,
            "median_total": 145.00,
            "p95_total": 450.00,
            "common_categories": ["apparel", "home", "beauty"],
        }),
        "sample_date": datetime.now() - timedelta(days=7),
    },
    {
        "domain": "ecommerce",
        "entity": "order",
        "anonymized_data": json.dumps({
            "order_id": "ORD-ANON-001",
            "status_distribution": {
                "pending": 0.15,
                "processing": 0.25,
                "shipped": 0.45,
                "delivered": 0.15,
            },
            "avg_processing_time_hours": 24,
        }),
        "distribution_stats": json.dumps({
            "avg_order_value": 125.50,
            "median_shipping_cost": 5.99,
            "express_shipping_rate": 0.35,
        }),
        "sample_date": datetime.now() - timedelta(days=14),
    },
]


async def seed_collections() -> None:
    """Seed all RAG collections with example data."""
    logger.info("seed_rag_starting")

    settings = Settings()
    client = WeaviateClient(settings)

    try:
        # Connect to Weaviate
        await client.connect()

        # Ensure collections exist
        await ensure_collections(client.client)

        # Seed TestDataPattern collection
        logger.info("seeding_test_data_patterns", count=len(TEST_DATA_PATTERNS))
        await client.batch_insert(
            collection=client.COLLECTION_PATTERNS,
            data_list=TEST_DATA_PATTERNS,
        )

        # Seed DefectPattern collection
        logger.info("seeding_defect_patterns", count=len(DEFECT_PATTERNS))
        await client.batch_insert(
            collection=client.COLLECTION_DEFECTS,
            data_list=DEFECT_PATTERNS,
        )

        # Seed ProductionSample collection
        logger.info("seeding_production_samples", count=len(PRODUCTION_SAMPLES))
        await client.batch_insert(
            collection=client.COLLECTION_PROD_SAMPLES,
            data_list=PRODUCTION_SAMPLES,
        )

        # Verify counts
        patterns_count = await client.count(client.COLLECTION_PATTERNS)
        defects_count = await client.count(client.COLLECTION_DEFECTS)
        prod_count = await client.count(client.COLLECTION_PROD_SAMPLES)

        logger.info(
            "seed_rag_complete",
            patterns=patterns_count,
            defects=defects_count,
            production_samples=prod_count,
        )

    except Exception as e:
        logger.error("seed_rag_error", error=str(e), exc_info=True)
        raise
    finally:
        await client.disconnect()


def main():
    """Main entry point for seeding script."""
    asyncio.run(seed_collections())


if __name__ == "__main__":
    main()
