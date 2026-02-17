"""Example adapter that returns mock search results.

This is what your adapter file should look like.
Replace this with actual calls to your search API.
"""

from veritail.types import SearchResponse, SearchResult


def search(query: str) -> SearchResponse:
    """
    This function must be named 'search' and return a SearchResponse.

    In a real adapter, you would:
    1. Call your search API with the query
    2. Parse the response
    3. Convert each result to a SearchResult object
    4. Wrap them in a SearchResponse
    """

    # Mock results - replace with real API calls
    mock_products = [
        {
            "product_id": "NIKE-001",
            "title": "Nike Air Max 90 Running Shoes",
            "description": "Classic running shoes with Air Max cushioning technology",
            "category": "Shoes > Running",
            "price": 129.99,
            "attributes": {"color": "black", "brand": "Nike", "size": "10"},
            "in_stock": True,
        },
        {
            "product_id": "NIKE-002",
            "title": "Nike Revolution 6 Running Shoes",
            "description": "Lightweight running shoes for daily training",
            "category": "Shoes > Running",
            "price": 64.99,
            "attributes": {"color": "red", "brand": "Nike", "size": "10"},
            "in_stock": True,
        },
        {
            "product_id": "ADIDAS-001",
            "title": "Adidas Ultraboost 22 Running Shoes",
            "description": "Premium running shoes with Boost cushioning",
            "category": "Shoes > Running",
            "price": 189.99,
            "attributes": {"color": "white", "brand": "Adidas", "size": "10"},
            "in_stock": True,
            "metadata": {"highlights": ["Free shipping", "Best seller"]},
        },
    ]

    # Convert to SearchResult objects
    results = []
    for i, product in enumerate(mock_products):
        results.append(
            SearchResult(
                product_id=product["product_id"],
                title=product["title"],
                description=product["description"],
                category=product["category"],
                price=product["price"],
                position=i,
                attributes=product["attributes"],
                in_stock=product["in_stock"],
                metadata=product.get("metadata", {}),
            )
        )

    return SearchResponse(results=results)
    # To report autocorrect / "did you mean" corrections, use:
    # return SearchResponse(results=results, corrected_query="corrected query text")
