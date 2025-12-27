"""Pre-defined entity schemas for common test data types."""

from test_data_agent.schemas.entities.cart import CART_SCHEMA
from test_data_agent.schemas.entities.cart_item import CART_ITEM_SCHEMA
from test_data_agent.schemas.entities.saved_cart import SAVED_CART_SCHEMA
from test_data_agent.schemas.entities.order import ORDER_SCHEMA
from test_data_agent.schemas.entities.order_item import ORDER_ITEM_SCHEMA
from test_data_agent.schemas.entities.order_status import ORDER_STATUS_SCHEMA
from test_data_agent.schemas.entities.payment import PAYMENT_SCHEMA
from test_data_agent.schemas.entities.refund import REFUND_SCHEMA
from test_data_agent.schemas.entities.payment_authorization import PAYMENT_AUTHORIZATION_SCHEMA
from test_data_agent.schemas.entities.product import PRODUCT_SCHEMA
from test_data_agent.schemas.entities.inventory import INVENTORY_SCHEMA
from test_data_agent.schemas.entities.stock import STOCK_SCHEMA
from test_data_agent.schemas.entities.stock_alert import STOCK_ALERT_SCHEMA
from test_data_agent.schemas.entities.user import USER_SCHEMA
from test_data_agent.schemas.entities.customer import CUSTOMER_SCHEMA
from test_data_agent.schemas.entities.loyalty_member import LOYALTY_MEMBER_SCHEMA
from test_data_agent.schemas.entities.customer_preferences import CUSTOMER_PREFERENCES_SCHEMA
from test_data_agent.schemas.entities.shipping import SHIPPING_SCHEMA
from test_data_agent.schemas.entities.shipment import SHIPMENT_SCHEMA
from test_data_agent.schemas.entities.tracking import TRACKING_SCHEMA
from test_data_agent.schemas.entities.discount import DISCOUNT_SCHEMA
from test_data_agent.schemas.entities.coupon import COUPON_SCHEMA
from test_data_agent.schemas.entities.promotion import PROMOTION_SCHEMA
from test_data_agent.schemas.entities.review import REVIEW_SCHEMA
from test_data_agent.schemas.entities.rating import RATING_SCHEMA
from test_data_agent.schemas.entities.wishlist import WISHLIST_SCHEMA
from test_data_agent.schemas.entities.favorites import FAVORITES_SCHEMA
from test_data_agent.schemas.entities.return_request import RETURN_SCHEMA
from test_data_agent.schemas.entities.exchange import EXCHANGE_SCHEMA
from test_data_agent.schemas.entities.analytics_event import ANALYTICS_EVENT_SCHEMA
from test_data_agent.schemas.entities.notification import NOTIFICATION_SCHEMA
from test_data_agent.schemas.entities.subscription import SUBSCRIPTION_SCHEMA
from test_data_agent.schemas.entities.gift_card import GIFT_CARD_SCHEMA
from test_data_agent.schemas.entities.search_query import SEARCH_QUERY_SCHEMA
from test_data_agent.schemas.entities.fraud_check import FRAUD_CHECK_SCHEMA
from test_data_agent.schemas.entities.support_ticket import SUPPORT_TICKET_SCHEMA

__all__ = [
    # Shopping Cart
    "CART_SCHEMA",
    "CART_ITEM_SCHEMA",
    "SAVED_CART_SCHEMA",
    # Orders
    "ORDER_SCHEMA",
    "ORDER_ITEM_SCHEMA",
    "ORDER_STATUS_SCHEMA",
    # Payments
    "PAYMENT_SCHEMA",
    "REFUND_SCHEMA",
    "PAYMENT_AUTHORIZATION_SCHEMA",
    # Catalog
    "PRODUCT_SCHEMA",
    "INVENTORY_SCHEMA",
    "STOCK_SCHEMA",
    "STOCK_ALERT_SCHEMA",
    # Users/Customers
    "USER_SCHEMA",
    "CUSTOMER_SCHEMA",
    "LOYALTY_MEMBER_SCHEMA",
    "CUSTOMER_PREFERENCES_SCHEMA",
    # Shipping
    "SHIPPING_SCHEMA",
    "SHIPMENT_SCHEMA",
    "TRACKING_SCHEMA",
    # Promotions
    "DISCOUNT_SCHEMA",
    "COUPON_SCHEMA",
    "PROMOTION_SCHEMA",
    # Reviews
    "REVIEW_SCHEMA",
    "RATING_SCHEMA",
    # Wishlist
    "WISHLIST_SCHEMA",
    "FAVORITES_SCHEMA",
    # Returns
    "RETURN_SCHEMA",
    "EXCHANGE_SCHEMA",
    # Analytics
    "ANALYTICS_EVENT_SCHEMA",
    # Communications
    "NOTIFICATION_SCHEMA",
    # Subscriptions
    "SUBSCRIPTION_SCHEMA",
    # Gift Cards
    "GIFT_CARD_SCHEMA",
    # Search
    "SEARCH_QUERY_SCHEMA",
    # Security
    "FRAUD_CHECK_SCHEMA",
    # Support
    "SUPPORT_TICKET_SCHEMA",
]
