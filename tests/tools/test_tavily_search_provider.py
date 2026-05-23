from app.tools.search import SearchResult


def test_search_result_keeps_url_title_and_content() -> None:
    result = SearchResult(
        url="https://example.com",
        title="Example",
        content="Body",
        provider="tavily",
    )

    assert result.url == "https://example.com"
    assert result.title == "Example"
    assert result.content == "Body"
