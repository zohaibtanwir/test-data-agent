"""Pre-defined entity schemas for common test data types."""

from test_data_agent.schemas.entities.cart import CART_SCHEMA
from test_data_agent.schemas.entities.order import ORDER_SCHEMA
from test_data_agent.schemas.entities.payment import PAYMENT_SCHEMA
from test_data_agent.schemas.entities.product import PRODUCT_SCHEMA
from test_data_agent.schemas.entities.review import REVIEW_SCHEMA
from test_data_agent.schemas.entities.user import USER_SCHEMA

__all__ = [
    "CART_SCHEMA",
    "ORDER_SCHEMA",
    "PAYMENT_SCHEMA",
    "PRODUCT_SCHEMA",
    "REVIEW_SCHEMA",
    "USER_SCHEMA",
]
