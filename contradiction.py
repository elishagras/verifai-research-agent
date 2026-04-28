import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def detect_contradictions(claims, sources):
    """Ask Claude to find contradictions across all claims and sources"""
    print("\n⚠️ Checking for contradictions...")

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""You are a fact-checking analyst specializing in finding contradictions.

Below are claims extracted from multiple sources. Your job is to identify cases where sources DISAGREE with each other on the same topic.

CLAIMS AND SOURCES:
{claims}

ALL SOURCE CONTENT:
{sources}

Find every contradiction where two or more sources give conflicting information on the same fact.

Respond in this EXACT format for each contradiction found:

TOPIC: [what the contradiction is about]
SOURCE_A: [first source URL]
CLAIM_A: [what source A says]
SOURCE_B: [second source URL]  
CLAIM_B: [what source B says]
SEVERITY: [HIGH / MEDIUM / LOW]
EXPLANATION: [one sentence explaining why this matters]
---

If no contradictions are found, respond with: NO_CONTRADICTIONS_FOUND"""
        }]
    )
    return response.content[0].text


def format_contradictions(raw_contradictions):
    """Format contradictions into readable output"""
    
    if "NO_CONTRADICTIONS_FOUND" in raw_contradictions:
        return "\n✅ No contradictions detected across sources.\n"

    blocks = raw_contradictions.strip().split("---")
    report = "\n## ⚠️ Contradictions Detected\n"
    report += "*These are cases where sources directly disagree — treat these claims with caution.*\n\n"

    count = 0
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        try:
            topic = block.split("TOPIC:")[1].split("SOURCE_A:")[0].strip()
            source_a = block.split("SOURCE_A:")[1].split("CLAIM_A:")[0].strip()
            claim_a = block.split("CLAIM_A:")[1].split("SOURCE_B:")[0].strip()
            source_b = block.split("SOURCE_B:")[1].split("CLAIM_B:")[0].strip()
            claim_b = block.split("CLAIM_B:")[1].split("SEVERITY:")[0].strip()
            severity = block.split("SEVERITY:")[1].split("EXPLANATION:")[0].strip()
            explanation = block.split("EXPLANATION:")[1].strip()

            # Severity emoji
            if severity == "HIGH":
                emoji = "🔴"
            elif severity == "MEDIUM":
                emoji = "🟡"
            else:
                emoji = "🟢"

            count += 1
            report += f"### {emoji} Contradiction {count}: {topic}\n"
            report += f"- **Source A** ({source_a}): {claim_a}\n"
            report += f"- **Source B** ({source_b}): {claim_b}\n"
            report += f"- **Severity:** {severity}\n"
            report += f"- **Why it matters:** {explanation}\n\n"

        except:
            continue

    if count == 0:
        return "\n✅ No contradictions detected across sources.\n"

    report += f"*{count} contradiction(s) found. Claims involved have been flagged.*\n"
    return report


def check_contradictions(claims, sources):
    """Main function"""
    raw = detect_contradictions(claims, sources)
    formatted = format_contradictions(raw)
    return formatted