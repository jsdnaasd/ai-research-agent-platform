from app.services.evidence import EvidenceGraph


def test_evidence_graph_groups_findings_by_brief() -> None:
    graph = EvidenceGraph()

    graph.add_finding("brief-1", "SMB pricing starts at $29", ["fragment-1", "fragment-2"])

    assert graph.findings_for_brief("brief-1") == ["SMB pricing starts at $29"]
