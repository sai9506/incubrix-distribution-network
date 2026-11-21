from app.rules.engine import PostingRulesEngine


def test_valid_content():
    engine = PostingRulesEngine()

    result = engine.evaluate({
        "title": "Python Tutorial",
        "body": "Learn Python programming.",
        "ai_generated": False
    })

    assert result["allowed"] is True


def test_frequency_limit():
    engine = PostingRulesEngine(max_posts_per_day=3)

    result = engine.evaluate(
        {"body": "Test content"},
        recent_posts=3
    )

    assert result["allowed"] is False


def test_self_promotion_disclosure():
    engine = PostingRulesEngine()

    result = engine.evaluate({
        "body": "Try my product",
        "is_self_promotion": True,
        "self_promo_disclosure": False
    })

    assert result["allowed"] is False


def test_ai_disclosure():
    engine = PostingRulesEngine()

    result = engine.evaluate({
        "body": "Generated article",
        "ai_generated": True,
        "ai_disclosure": False
    })

    assert result["allowed"] is False


def test_link_limit():
    engine = PostingRulesEngine(max_links=2)

    result = engine.evaluate({
        "body": (
            "Visit https://a.com "
            "https://b.com https://c.com"
        )
    })

    assert result["allowed"] is False