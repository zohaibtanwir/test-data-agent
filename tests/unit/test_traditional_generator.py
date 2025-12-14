"""Unit tests for traditional generator."""

import pytest

from test_data_agent.generators.traditional import TraditionalGenerator
from test_data_agent.proto import test_data_pb2


@pytest.fixture
def generator():
    """Fixture for traditional generator."""
    return TraditionalGenerator()


@pytest.mark.asyncio
async def test_generate_cart(generator):
    """Test generating cart data."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-001",
        domain="ecommerce",
        entity="cart",
        count=5,
    )

    result = await generator.generate(request)

    assert len(result.data) == 5
    assert result.metadata["generation_path"] == "traditional"

    # Check first cart has required fields
    cart = result.data[0]
    assert "cart_id" in cart
    assert "customer_id" in cart
    assert "items" in cart
    assert "subtotal" in cart
    assert "tax" in cart
    assert "total" in cart
    assert "_index" in cart
    assert "_scenario" in cart


@pytest.mark.asyncio
async def test_generate_order(generator):
    """Test generating order data."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-002",
        domain="ecommerce",
        entity="order",
        count=3,
    )

    result = await generator.generate(request)

    assert len(result.data) == 3

    order = result.data[0]
    assert "order_id" in order
    assert "customer_id" in order
    assert "items" in order
    assert "shipping_address" in order
    assert "payment_method" in order
    assert "status" in order


@pytest.mark.asyncio
async def test_generate_payment(generator):
    """Test generating payment data."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-003",
        domain="ecommerce",
        entity="payment",
        count=3,
    )

    result = await generator.generate(request)

    assert len(result.data) == 3

    payment = result.data[0]
    assert "payment_id" in payment
    assert "order_id" in payment
    assert "method" in payment
    assert "amount" in payment
    assert "currency" in payment
    assert "status" in payment


@pytest.mark.asyncio
async def test_generate_user(generator):
    """Test generating user data."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-004",
        domain="ecommerce",
        entity="user",
        count=3,
    )

    result = await generator.generate(request)

    assert len(result.data) == 3

    user = result.data[0]
    assert "user_id" in user
    assert "email" in user
    assert "first_name" in user
    assert "last_name" in user
    assert "created_at" in user


@pytest.mark.asyncio
async def test_generate_review(generator):
    """Test generating review data."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-005",
        domain="ecommerce",
        entity="review",
        count=3,
    )

    result = await generator.generate(request)

    assert len(result.data) == 3

    review = result.data[0]
    assert "review_id" in review
    assert "product_id" in review
    assert "user_id" in review
    assert "rating" in review
    assert 1 <= review["rating"] <= 5
    assert "title" in review
    assert "body" in review


@pytest.mark.asyncio
async def test_respects_constraints(generator):
    """Test that generator respects field constraints."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-006",
        domain="ecommerce",
        entity="review",
        count=10,
    )

    result = await generator.generate(request)

    for review in result.data:
        # Rating should be 1-5
        assert 1 <= review["rating"] <= 5

        # Title should have reasonable length
        assert len(review["title"]) >= 5

        # Helpful votes should be non-negative
        assert review["helpful_votes"] >= 0


@pytest.mark.asyncio
async def test_scenario_distribution(generator):
    """Test that records are distributed across scenarios."""
    scenario1 = test_data_pb2.Scenario(name="happy_path", count=7)
    scenario2 = test_data_pb2.Scenario(name="edge_case", count=3)

    request = test_data_pb2.GenerateRequest(
        request_id="test-007",
        domain="ecommerce",
        entity="cart",
        count=10,
        scenarios=[scenario1, scenario2],
    )

    result = await generator.generate(request)

    assert len(result.data) == 10

    # Count scenarios
    happy_count = sum(1 for r in result.data if r["_scenario"] == "happy_path")
    edge_count = sum(1 for r in result.data if r["_scenario"] == "edge_case")

    assert happy_count == 7
    assert edge_count == 3


@pytest.mark.asyncio
async def test_streaming_batches(generator):
    """Test streaming generation in batches."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-008",
        domain="ecommerce",
        entity="user",
        count=25,
    )

    batches = []
    async for batch in generator.generate_stream(request, batch_size=10):
        batches.append(batch)

    # Should have 3 batches (10, 10, 5)
    assert len(batches) == 3
    assert len(batches[0].data) == 10
    assert len(batches[1].data) == 10
    assert len(batches[2].data) == 5


@pytest.mark.asyncio
async def test_supports_all_requests(generator):
    """Test that traditional generator supports any request."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-009",
        domain="ecommerce",
        entity="cart",
        count=5,
    )

    assert generator.supports(request) is True


@pytest.mark.asyncio
async def test_metadata_fields_added(generator):
    """Test that _index and _scenario are added to records."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-010",
        domain="ecommerce",
        entity="cart",
        count=5,
    )

    result = await generator.generate(request)

    for idx, record in enumerate(result.data):
        assert record["_index"] == idx
        assert "_scenario" in record


@pytest.mark.asyncio
async def test_nested_objects_generated(generator):
    """Test that nested objects are properly generated."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-011",
        domain="ecommerce",
        entity="order",
        count=1,
    )

    result = await generator.generate(request)
    order = result.data[0]

    # Check shipping_address is an object
    assert isinstance(order["shipping_address"], dict)
    assert "street" in order["shipping_address"]
    assert "city" in order["shipping_address"]
    assert "state" in order["shipping_address"]
    assert "zip" in order["shipping_address"]


@pytest.mark.asyncio
async def test_arrays_generated(generator):
    """Test that arrays are properly generated."""
    request = test_data_pb2.GenerateRequest(
        request_id="test-012",
        domain="ecommerce",
        entity="cart",
        count=1,
    )

    result = await generator.generate(request)
    cart = result.data[0]

    # Check items is an array
    assert isinstance(cart["items"], list)
    assert len(cart["items"]) > 0

    # Check item structure
    item = cart["items"][0]
    assert "sku" in item
    assert "name" in item
    assert "quantity" in item
    assert "price" in item
