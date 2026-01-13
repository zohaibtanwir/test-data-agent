"""Coherence scoring for generated test data."""

from datetime import datetime

from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


class CoherenceScorer:
    """Scores the coherence and realism of generated data."""

    # Category affinity groups - items that make sense together
    CATEGORY_GROUPS = {
        "fitness": {
            "running shoes",
            "athletic socks",
            "water bottle",
            "fitness tracker",
            "gym bag",
            "yoga mat",
        },
        "beauty": {"lipstick", "mascara", "foundation", "brushes", "makeup remover", "face cream"},
        "home": {"bedding", "pillows", "blankets", "candles", "throw pillows", "sheets"},
        "baby": {"onesies", "blanket", "stuffed animal", "baby clothes", "diapers", "bottles"},
        "date_night": {"dress", "heels", "clutch", "jewelry", "perfume", "earrings"},
        "office": {"blazer", "dress shirt", "slacks", "tie", "belt", "dress shoes"},
        "casual": {"jeans", "t-shirt", "sneakers", "hoodie", "backpack", "cap"},
        "kitchen": {"cookware", "utensils", "dishes", "glassware", "cutting board", "knives"},
    }

    def score(self, data: dict, entity_type: str) -> float:
        """Score the coherence of a generated record.

        Args:
            data: Generated record
            entity_type: Type of entity (cart, order, etc.)

        Returns:
            Coherence score from 0.0 to 1.0
        """
        if entity_type == "cart":
            return self.score_cart(data)
        elif entity_type == "order":
            return self.score_order(data)
        else:
            # Calculate actual coherence score for generic entities
            return self.score_generic(data, entity_type)

    def score_cart(self, cart: dict) -> float:
        """Score cart coherence.

        Args:
            cart: Cart record

        Returns:
            Coherence score (0.0 to 1.0)
        """
        scores = []

        # 1. Category affinity (0-0.3)
        category_score = self._score_category_affinity(cart.get("items", []))
        scores.append(("category_affinity", category_score, 0.3))

        # 2. Reasonable quantities (0-0.2)
        quantity_score = self._score_quantities(cart.get("items", []))
        scores.append(("quantities", quantity_score, 0.2))

        # 3. Math correctness: subtotal + tax = total (0-0.3)
        math_score = self._score_cart_math(cart)
        scores.append(("math", math_score, 0.3))

        # 4. Chronological dates (0-0.2)
        date_score = self._score_dates(cart)
        scores.append(("dates", date_score, 0.2))

        # Calculate weighted total
        total = sum(score * weight for _, score, weight in scores)

        logger.debug(
            "cart_coherence_scored",
            total=total,
            breakdown={name: score for name, score, _ in scores},
        )

        return total

    def score_order(self, order: dict) -> float:
        """Score order coherence.

        Args:
            order: Order record

        Returns:
            Coherence score (0.0 to 1.0)
        """
        scores = []

        # 1. Category affinity
        category_score = self._score_category_affinity(order.get("items", []))
        scores.append(("category_affinity", category_score, 0.25))

        # 2. Reasonable quantities
        quantity_score = self._score_quantities(order.get("items", []))
        scores.append(("quantities", quantity_score, 0.15))

        # 3. Math correctness (more complex for orders)
        math_score = self._score_order_math(order)
        scores.append(("math", math_score, 0.3))

        # 4. Chronological dates (more important for orders)
        date_score = self._score_dates(order)
        scores.append(("dates", date_score, 0.3))

        total = sum(score * weight for _, score, weight in scores)

        logger.debug(
            "order_coherence_scored",
            total=total,
            breakdown={name: score for name, score, _ in scores},
        )

        return total

    def _score_category_affinity(self, items: list[dict]) -> float:
        """Score how well items belong together.

        Args:
            items: List of item dicts

        Returns:
            Score from 0.0 to 1.0
        """
        if not items or len(items) < 2:
            return 1.0  # Single item carts are coherent by definition

        # Extract item names/categories
        item_names = []
        for item in items:
            name = item.get("name", "").lower()
            category = item.get("category", "").lower()
            item_names.append(name if name else category)

        if not item_names:
            return 0.5  # Neutral if no names

        # Check if items match any affinity group
        max_match = 0
        for group_name, group_items in self.CATEGORY_GROUPS.items():
            matches = sum(1 for name in item_names if any(g in name for g in group_items))
            match_ratio = matches / len(item_names)
            max_match = max(max_match, match_ratio)

        # Scale to 0-1
        # High match (>80%) = 1.0
        # Medium match (50%) = 0.6
        # Low match (<30%) = 0.3
        # No match = 0.2 (still possible but random)

        if max_match >= 0.8:
            return 1.0
        elif max_match >= 0.5:
            return 0.6
        elif max_match >= 0.3:
            return 0.4
        else:
            return 0.2

    def _score_quantities(self, items: list[dict]) -> float:
        """Score if item quantities are reasonable.

        Args:
            items: List of item dicts

        Returns:
            Score from 0.0 to 1.0
        """
        if not items:
            return 1.0

        reasonable = 0
        total = 0

        for item in items:
            qty = item.get("quantity", 1)
            total += 1

            # Reasonable quantities are 1-10 for most items
            if 1 <= qty <= 10:
                reasonable += 1
            # Very high quantities (>20) are suspicious
            elif qty > 20:
                reasonable += 0.2
            # Zero or negative is wrong
            elif qty <= 0:
                reasonable += 0
            else:
                # 11-20 is borderline
                reasonable += 0.7

        return reasonable / total if total > 0 else 1.0

    def _score_cart_math(self, cart: dict) -> float:
        """Score cart mathematical consistency.

        Args:
            cart: Cart record

        Returns:
            Score from 0.0 to 1.0
        """
        subtotal = cart.get("subtotal", 0)
        tax = cart.get("tax", 0)
        total = cart.get("total", 0)

        # Check if total = subtotal + tax (within 0.01 tolerance for floating point)
        expected_total = subtotal + tax
        if abs(total - expected_total) < 0.01:
            return 1.0
        # Close but not exact
        elif abs(total - expected_total) < 1.0:
            return 0.7
        # Way off
        else:
            return 0.0

    def _score_order_math(self, order: dict) -> float:
        """Score order mathematical consistency.

        Args:
            order: Order record

        Returns:
            Score from 0.0 to 1.0
        """
        # Orders have more complex math: subtotal + tax + shipping - discount = total
        subtotal = order.get("subtotal", 0)
        tax = order.get("tax", 0)
        shipping = order.get("shipping_cost", 0)
        discount = order.get("discount", 0)
        total = order.get("total", 0)

        expected_total = subtotal + tax + shipping - discount

        if abs(total - expected_total) < 0.01:
            return 1.0
        elif abs(total - expected_total) < 1.0:
            return 0.7
        else:
            return 0.0

    def _score_dates(self, record: dict) -> float:
        """Score chronological validity of dates.

        Args:
            record: Record with date fields

        Returns:
            Score from 0.0 to 1.0
        """
        # Common date fields
        date_fields = ["created_at", "updated_at", "completed_at", "modified_at", "shipped_at"]

        dates = {}
        for field in date_fields:
            if field in record:
                value = record[field]
                try:
                    if isinstance(value, str):
                        # Try parsing ISO format
                        dates[field] = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    elif isinstance(value, datetime):
                        dates[field] = value
                except (ValueError, AttributeError):
                    continue

        if not dates:
            return 1.0  # No dates to validate

        # Check chronological order
        # created <= updated <= completed/shipped
        score = 1.0

        if "created_at" in dates and "updated_at" in dates:
            if dates["created_at"] > dates["updated_at"]:
                score -= 0.5

        if "updated_at" in dates and "completed_at" in dates:
            if dates["updated_at"] > dates["completed_at"]:
                score -= 0.5

        if "created_at" in dates and "shipped_at" in dates:
            if dates["created_at"] > dates["shipped_at"]:
                score -= 0.5

        return max(0.0, score)

    def score_generic(self, data: dict, entity_type: str) -> float:
        """Score coherence for generic entity types.

        Evaluates:
        - Data completeness (non-empty values)
        - Type consistency (values match expected types)
        - Value validity (no obvious invalid data)
        - Date coherence (chronological order)

        Args:
            data: Generated record
            entity_type: Type of entity

        Returns:
            Coherence score from 0.0 to 1.0
        """
        if not data:
            return 0.0

        scores = []

        # 1. Completeness score (0.3 weight) - non-empty meaningful values
        completeness = self._score_completeness(data)
        scores.append(("completeness", completeness, 0.3))

        # 2. Type consistency (0.25 weight) - values are proper types
        type_consistency = self._score_type_consistency(data)
        scores.append(("type_consistency", type_consistency, 0.25))

        # 3. Value validity (0.25 weight) - values are reasonable
        value_validity = self._score_value_validity(data)
        scores.append(("value_validity", value_validity, 0.25))

        # 4. Date coherence (0.2 weight) - dates are chronologically valid
        date_coherence = self._score_dates(data)
        scores.append(("date_coherence", date_coherence, 0.2))

        # Calculate weighted total
        total = sum(score * weight for _, score, weight in scores)

        logger.debug(
            "generic_coherence_scored",
            entity_type=entity_type,
            total=total,
            breakdown={name: round(score, 2) for name, score, _ in scores},
        )

        return total

    def _score_completeness(self, data: dict) -> float:
        """Score data completeness.

        Args:
            data: Record data

        Returns:
            Score from 0.0 to 1.0
        """
        if not data:
            return 0.0

        total_fields = len(data)
        if total_fields == 0:
            return 0.0

        complete_fields = 0
        for key, value in data.items():
            # Skip internal metadata fields
            if key.startswith("_"):
                total_fields -= 1
                continue

            # Check if value is non-empty and meaningful
            if value is None:
                continue
            elif isinstance(value, str) and value.strip() == "":
                continue
            elif isinstance(value, (list, dict)) and len(value) == 0:
                continue
            else:
                complete_fields += 1

        return complete_fields / total_fields if total_fields > 0 else 1.0

    def _score_type_consistency(self, data: dict) -> float:
        """Score type consistency of values.

        Args:
            data: Record data

        Returns:
            Score from 0.0 to 1.0
        """
        if not data:
            return 1.0

        # Type expectations based on common field name patterns
        type_expectations = {
            "id": (str, int),
            "name": (str,),
            "email": (str,),
            "phone": (str,),
            "price": (int, float),
            "cost": (int, float),
            "amount": (int, float),
            "total": (int, float),
            "subtotal": (int, float),
            "tax": (int, float),
            "quantity": (int,),
            "count": (int,),
            "date": (str,),
            "time": (str,),
            "created": (str,),
            "updated": (str,),
            "status": (str,),
            "type": (str,),
            "description": (str,),
            "address": (str, dict),
            "items": (list,),
            "enabled": (bool,),
            "active": (bool,),
            "is_": (bool,),
            "has_": (bool,),
        }

        total_checked = 0
        consistent = 0

        for key, value in data.items():
            if key.startswith("_") or value is None:
                continue

            # Find matching type expectation
            key_lower = key.lower()
            expected_types = None

            for pattern, types in type_expectations.items():
                if pattern in key_lower or key_lower.endswith(pattern):
                    expected_types = types
                    break

            if expected_types:
                total_checked += 1
                if isinstance(value, expected_types):
                    consistent += 1

        return consistent / total_checked if total_checked > 0 else 1.0

    def _score_value_validity(self, data: dict) -> float:
        """Score validity of values (reasonable ranges, formats).

        Args:
            data: Record data

        Returns:
            Score from 0.0 to 1.0
        """
        if not data:
            return 1.0

        total_checked = 0
        valid = 0

        for key, value in data.items():
            if key.startswith("_") or value is None:
                continue

            key_lower = key.lower()

            # Check numeric values are reasonable
            if isinstance(value, (int, float)):
                total_checked += 1
                if "price" in key_lower or "cost" in key_lower or "amount" in key_lower:
                    # Prices should be positive and reasonable (not > $1M typically)
                    if 0 <= value <= 1000000:
                        valid += 1
                elif "quantity" in key_lower or "count" in key_lower:
                    # Quantities should be positive integers, typically < 1000
                    if 0 <= value <= 10000:
                        valid += 1
                elif "percent" in key_lower or "rate" in key_lower:
                    # Percentages/rates usually 0-100 or 0-1
                    if 0 <= value <= 100:
                        valid += 1
                else:
                    # Generic numeric - just check it's not absurdly large
                    if -1e12 <= value <= 1e12:
                        valid += 1

            # Check string values
            elif isinstance(value, str):
                # Check email format if field suggests email
                if "email" in key_lower:
                    total_checked += 1
                    if "@" in value and "." in value:
                        valid += 1
                # Check phone has digits
                elif "phone" in key_lower:
                    total_checked += 1
                    digits = sum(1 for c in value if c.isdigit())
                    if digits >= 7:  # Minimum phone digits
                        valid += 1
                # Check status values are reasonable length
                elif "status" in key_lower:
                    total_checked += 1
                    if 1 <= len(value) <= 50:
                        valid += 1

        return valid / total_checked if total_checked > 0 else 1.0
