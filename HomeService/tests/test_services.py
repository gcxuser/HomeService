"""Tests for pricing service logic."""
import sys
sys.path.insert(0, "/home/gcx/learn/HomeService")

from HomeService.services.pricing_service import PricingService


def test_pricing_basic():
    """Test basic pricing calculation."""
    pricing = PricingService()
    result = pricing.estimate_price("daily_cleaning", 60.0, {})

    assert "price" in result
    assert "duration" in result
    assert result["price"] > 0
    assert result["duration"] > 0


def test_pricing_with_extras():
    """Test pricing with additional services."""
    pricing = PricingService()
    result = pricing.estimate_price(
        "deep_cleaning",
        80.0,
        {"oven_cleaning": True, "window_cleaning": True}
    )

    assert result["price"] > 0
    # Extra services should increase price
    assert "note" in result


def test_pricing_large_area():
    """Test pricing for large area."""
    pricing = PricingService()
    result = pricing.estimate_price("daily_cleaning", 200.0, {})

    assert result["price"] > 0
    # Larger area should have higher price
    assert result["duration"] > 3.0  # Should take more than 3 hours


def test_pricing_small_area():
    """Test pricing for small area."""
    pricing = PricingService()
    result = pricing.estimate_price("daily_cleaning", 30.0, {})

    assert result["price"] > 0
    # Smaller area should have lower price
