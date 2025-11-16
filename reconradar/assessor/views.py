from django.shortcuts import render
from django.utils.safestring import mark_safe
from .gemini import assess, split
from .database import fetch_cache
import json
import markdown


def sanitize_section(text):
    """
    Very minimal sanity check:
    - None → "No data"
    - Empty → "No data"
    """
    if not text or not text.strip():
        return "No data"
    return text.strip()


def index(request):

    metadata = {
        "category": "-",
        "site": "-",
        "vendor": "-",
        "name_version": "-"
    }

    security_result = "Awaiting input."
    compliance_result = "Awaiting input."
    alternatives_result = "Awaiting input."
    summary_result = "Awaiting input."
    score_dict = {
        "security": 0,
        "compliance": 0,
        "reputation": 0,
        "controls": 0,
        "privacy": 0,
        "reliability": 0
    }

    # ---- Manual suitability score override for testing ----
    manual_score = request.GET.get("manual_score", "75")

    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        if query:
            # Call Gemini + split + validate
            try:
                response = fetch_cache(query)
                if not response:
                    content = assess(query)
                else:
                    content = response.to_content()
                parts, parsed_scores, metadata = split(content)

                # Markdown-render the first 4
                security_result = mark_safe(markdown.markdown(parts[0]))
                compliance_result = mark_safe(markdown.markdown(parts[1]))
                alternatives_result = mark_safe(markdown.markdown(parts[2]))
                summary_result = mark_safe(markdown.markdown(parts[3]))

                # Validate radar scores
                score_dict.update(parsed_scores)

            except Exception as e:
                security_result = f"Error: {e}"
                compliance_result = f"Error: {e}"
                alternatives_result = f"Error: {e}"
                summary_result = f"Error: {e}"

    return render(request, "assessor/index.html", {
        'security_result': security_result,
        'compliance_result': compliance_result,
        'alternatives_result': alternatives_result,
        'summary_result': summary_result,
        'scores': score_dict,
        'manual_score': manual_score,
        'metadata': metadata
    })
