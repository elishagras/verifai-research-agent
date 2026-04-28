import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Source credibility rules
SOURCE_TIERS = {
    "HIGH": [
        "reuters.com", "bloomberg.com", "wsj.com", "ft.com",
        "techcrunch.com", "theverge.com", "wired.com",
        "forbes.com", "businessinsider.com", "cnbc.com",
        "sec.gov", "gov", "edu", "nature.com", "arxiv.org"
    ],
    "MEDIUM": [
        "medium.com", "substack.com", "linkedin.com",
        "wikipedia.org", "investopedia.com", "crunchbase.com",
        "statista.com", "electroiq.com", "getlatka.com"
    ],
    "LOW": [
        "youtube.com", "reddit.com", "quora.com",
        "tiktok.com", "facebook.com", "twitter.com",
        "x.com", "blogspot.com", "wordpress.com"
    ]
}

def score_source(url):
    """Score a single source URL by credibility"""
    url_lower = url.lower()

    # Check HIGH tier
    for domain in SOURCE_TIERS["HIGH"]:
        if domain in url_lower:
            return "HIGH", "⭐⭐⭐", "Established news outlet or academic source"

    # Check LOW tier first to catch social/blogs
    for domain in SOURCE_TIERS["LOW"]:
        if domain in url_lower:
            return "LOW", "⭐", "Social media or user-generated content"

    # Check MEDIUM tier
    for domain in SOURCE_TIERS["MEDIUM"]:
        if domain in url_lower:
            return "MEDIUM", "⭐⭐", "General reference or aggregator site"

    # Default unknown
    return "MEDIUM", "⭐⭐", "Unknown source - credibility unverified"


def score_all_sources(sources_text):
    """Extract URLs from sources and score each one"""
    print("\n🌐 Scoring source quality...")

    # Extract URLs
    urls = []
    for line in sources_text.split("\n"):
        line = line.strip()
        if line.startswith("http"):
            url = line.split()[0]
            urls.append(url)
        elif line.startswith("Source:"):
            url = line.replace("Source:", "").strip()
            if url.startswith("http"):
                urls.append(url)

    if not urls:
        return "\n⚠️ No sources found to score.\n"

    # Score each URL
    report = "\n## 🌐 Source Quality Ratings\n"
    report += "*Higher quality sources carry more weight in confidence scoring.*\n\n"

    high_count = 0
    medium_count = 0
    low_count = 0

    seen = set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)

        tier, stars, reason = score_source(url)

        if tier == "HIGH":
            high_count += 1
        elif tier == "MEDIUM":
            medium_count += 1
        else:
            low_count += 1

        # Shorten URL for display
        display_url = url[:60] + "..." if len(url) > 60 else url

        report += f"**{stars} {tier}** - {display_url}\n"
        report += f"   _{reason}_\n\n"

    # Summary
    total = high_count + medium_count + low_count
    report += "---\n"
    report += f"**Source Summary:** {total} sources - "
    report += f"⭐⭐⭐ High: {high_count} | "
    report += f"⭐⭐ Medium: {medium_count} | "
    report += f"⭐ Low: {low_count}\n"

    if high_count == 0:
        report += "\n⚠️ **Warning:** No high-credibility sources found. "
        report += "Consider verifying findings with established news outlets.\n"
    elif high_count >= 3:
        report += "\n✅ **Good:** Multiple high-credibility sources found. "
        report += "Findings are well supported.\n"

    return report