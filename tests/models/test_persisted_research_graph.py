from app.models.source_fragment import ResearchSourceFragment


def test_source_fragment_keeps_text_and_offsets() -> None:
    fragment = ResearchSourceFragment(
        source_id="source-1",
        content="Pricing starts at $29",
        citation_label="fragment-1",
        offset_start=0,
        offset_end=21,
    )

    assert fragment.citation_label == "fragment-1"
    assert fragment.offset_end == 21
