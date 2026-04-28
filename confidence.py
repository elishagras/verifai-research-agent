import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def score_claims(findings, sources):
    """Ask Claude to extract claims and score each one"""
    print("\n🎯 Scoring claims by confidence...")

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""You are a fact-checking analyst. Your job is to extract every factual claim from the findings and score each one.

FINDINGS:
{findings}

SOURCES USED:
{sources}

For each claim, apply this scoring rubric:
- HIGH: Claim is confirmed by 2 or more independent sources
- MEDIUM: Claim comes from a single credible source
- LOW: Claim is inferred, estimated, or from a low-authority source

Respond in this EXACT format for each claim:

CLAIM: [the specific factual claim]
SCORE: [HIGH / MEDIUM / LOW]
REASON: [one sentence explaining the score]
SOURCE: [the URL that supports it, or "inferred" if none]
---

Extract every factual claim. Be thorough."""
        }]
    )
    return response.content[0].text


def format_scored_report(scored_claims):
    """Format the scored claims into a readable report"""
    lines = scored_claims.strip().split("---")
    report = "\n## Confidence-Scored Claims\n"

    for block in lines:
        block = block.strip()
        if not block:
            continue

        # Add emoji based on score
        if "SCORE: HIGH" in block:
            emoji = "🟢"
        elif "SCORE: MEDIUM" in block:
            emoji = "🟡"
        elif "SCORE: LOW" in block:
            emoji = "🔴"
        else:
            continue

        # Extract parts
        try:
            claim = block.split("CLAIM:")[1].split("SCORE:")[0].strip()
            score = block.split("SCORE:")[1].split("REASON:")[0].strip()
            reason = block.split("REASON:")[1].split("SOURCE:")[0].strip()
            source = block.split("SOURCE:")[1].strip()

            report += f"\n{emoji} **{score}** — {claim}\n"
            report += f"   _{reason}_\n"
            report += f"   📎 {source}\n"
        except:
            continue

    return report


def score_report(findings, sources):
    """Main function — takes findings and sources, returns scored report"""
    raw_scores = score_claims(findings, sources)
    formatted = format_scored_report(raw_scores)
    return formatted