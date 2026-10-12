from research_agent.tools import html_to_text, select_passages

PAGE = """
<html><body>
<section><p>Lead paragraph about <b>Jevons</b>.<sup class="reference">[1]</sup></p>
<table class="infobox"><tr><th>Died</th><td>13 August 1882</td></tr></table></section>
<section><h2>Premiers</h2>
<table><tr><th>Name</th><th>From</th><th>To</th></tr>
<tr><td><p>Gladstone</p></td><td>1880</td><td>1885</td></tr></table>
<ul><li>A bullet<ul><li>nested</li></ul></li></ul></section>
<section><h2>References</h2><p>Should be dropped</p></section>
</body></html>
"""


def test_html_to_text_keeps_tables_and_drops_noise():
    text = html_to_text(PAGE)
    assert "Died | 13 August 1882" in text  # infobox row
    assert "Gladstone | 1880 | 1885" in text  # table row, nested <p> not duplicated
    assert text.count("Gladstone") == 1
    assert "## Premiers" in text
    assert "- A bullet nested" in text and text.count("nested") == 1
    assert "[1]" not in text
    assert "Should be dropped" not in text


def test_select_passages_keeps_lead_and_relevant_chunks():
    lead = "Lead section. " * 20
    filler = [f"Unrelated paragraph {i} about weather and cooking." * 5 for i in range(40)]
    target = "Gladstone held office from 1880 to 1885."
    text = "\n".join([lead, *filler[:20], target, *filler[20:]])

    out = select_passages(text, "prime minister 1882 Gladstone", max_chars=1500,
                          chunk_chars=300, lead_chars=300)
    assert len(out) <= 1500 + 50
    assert out.startswith("Lead section.")
    assert target in out
    assert "[...]" in out


def test_select_passages_short_text_untouched():
    assert select_passages("short", "anything", 100) == "short"
