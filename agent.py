import os
from dotenv import load_dotenv
import anthropic
from tavily import TavilyClient
from confidence import score_report
from contradiction import check_contradictions
from source_quality import score_all_sources
import streamlit as st

# Load API keys
load_dotenv()

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query):
    """Search the web using Tavily"""
    print(f"\n🔍 Searching: {query}")
    try:
        results = tavily.search(query=query, max_results=3)
        
        # Check if results are empty
        if not results or "results" not in results or len(results["results"]) == 0:
            print("⚠️ No results found for this query")
            return []
        
        return results["results"]
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        return []

def format_sources(search_results):
    """Format search results into readable text"""
    sources_text = ""
    for r in search_results:
        sources_text += f"\nSource: {r['url']}\nContent: {r['content']}\n"
    return sources_text

def analyze(question, all_sources):
    """Ask Claude to analyze findings and identify gaps"""
    print("\n🤖 Claude is analyzing findings...")

    try:
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""You are a competitive intelligence analyst.

Research question: {question}

Here are all the sources collected so far:
{all_sources}

Respond in this EXACT format:

FINDINGS:
[Write your key findings here]

GAPS:
[List what is still unknown or missing. Be specific.]

NEXT_SEARCH:
[If there are gaps, write ONE specific search query to find the missing info. 
If you have enough information, write NONE]"""
            }]
        )
        return response.content[0].text
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return f"FINDINGS:\nError during analysis: {str(e)}\n\nGAPS:\nUnable to complete analysis\n\nNEXT_SEARCH:\nNONE"

def parallel_search(queries):
    """Run multiple searches simultaneously"""
    all_sources = ""
    for query in queries:
        print(f"\n🔍 Parallel Search: {query}")
        results = search(query)
        if results:
            all_sources += format_sources(results)
    return all_sources

def generate_parallel_queries(question):
    """Ask Claude to generate 4 search queries all at once"""
    print("\n🤖 Claude is planning parallel searches...")

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""You are a research strategist.

For this research question: {question}

Generate exactly 4 different search queries that together give BROAD coverage of the topic.
Each query should cover a different angle:
1. Overall strategy and market position
2. Financial performance and metrics
3. Main competitors and competitive landscape
4. Recent news and developments

Respond in this EXACT format:
QUERY1: [search query]
QUERY2: [search query]
QUERY3: [search query]
QUERY4: [search query]"""
        }]
    )

    # Parse queries
    queries = []
    for line in response.content[0].text.split("\n"):
        if line.startswith("QUERY"):
            query = line.split(":", 1)[1].strip()
            queries.append(query)
    return queries

def generate_final_report(question, all_sources):
    """Generate the final structured report"""
    print("\n📝 Generating final report...")

    # Check if we have any sources at all
    if not all_sources or all_sources.strip() == "":
        return f"""# Research Report: {question}

## Executive Summary
Unable to generate report - no sources were found during research.

## Key Findings
No data available.

## Competitive Landscape
No information found.

## Gaps & Limitations
Complete information gap - search queries returned no results. This could mean:
- The topic is too niche or specific
- The query terms may need to be adjusted
- The information may not be publicly available

## Sources
None found."""

    try:
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""You are a competitive intelligence analyst. 
Based on all research collected, write a comprehensive final report.

Research question: {question}

All sources:
{all_sources}

Write a structured report with:
# Research Report: [Topic]

## Executive Summary
[2-3 sentence overview]

## Key Findings
[Detailed findings with specific facts]

## Competitive Landscape
[Who the competitors are and how they differ]

## Gaps & Limitations
[What could not be determined from available sources]

## Sources
[List all URLs used]"""
            }]
        )
        return response.content[0].text
    except Exception as e:
        return f"""# Research Report: {question}

## Executive Summary
Error generating report: API request failed.

## Error Details
{str(e)}

## Sources Collected
{len(all_sources.split('Source:')) - 1} sources were found but report generation failed.

Please try again or contact support if the issue persists."""

def run_agent_ui(question, status, iteration_log):
    """Iterative version - searches step by step"""
    all_sources = ""
    iteration = 0
    current_query = question

    while iteration < 4:
        iteration += 1
        status.info(f"🔄 Iteration {iteration} of 4 - Searching: *{current_query}*")

        with iteration_log:
            st.write(f"**🔍 Search {iteration}:** {current_query}")

        # Search
        results = search(current_query)
        
        # Handle empty results
        if not results or len(results) == 0:
            with iteration_log:
                st.warning(f"⚠️ No results found for: {current_query}")
            # Try to continue with what we have
            break
        
        new_sources = format_sources(results)
        all_sources += new_sources

        # Analyze
        analysis = analyze(question, all_sources)

        with iteration_log:
            with st.expander(f"📊 Analysis {iteration}"):
                st.text(analysis)

        # Check if done
        if "NEXT_SEARCH:\nNONE" in analysis or "NEXT_SEARCH: NONE" in analysis:
            break

        try:
            next_query = analysis.split("NEXT_SEARCH:")[1].strip()
            if not next_query or next_query.upper() == "NONE":
                break
            current_query = next_query
        except:
            break

    status.success("✅ Research complete!")

    # Generate report
    final_report = generate_final_report(question, all_sources)

    # Score claims
    scored = score_report(final_report, all_sources)

    # Detect contradictions
    contradictions = check_contradictions(final_report, all_sources)

    # Source quality
    source_quality = score_all_sources(all_sources)

    return {
        "report": final_report,
        "scores": scored,
        "contradictions": contradictions,
        "source_quality": source_quality
    }

def run_agent_parallel_ui(question, status, iteration_log):
    """Parallel version - searches broadly all at once"""

    status.info("🤖 Planning parallel search strategy...")

    # Generate all queries at once
    queries = generate_parallel_queries(question)

    with iteration_log:
        st.write("**🌐 Parallel Search Strategy - searching all angles at once:**")
        for i, q in enumerate(queries, 1):
            st.write(f"**🔍 Query {i}:** {q}")

    status.info("⚡ Running all searches simultaneously...")

    # Run all searches
    all_sources = parallel_search(queries)
    
    # Check if we got any sources
    if not all_sources or all_sources.strip() == "":
        with iteration_log:
            st.error("❌ No sources found across all searches. Try a different query.")
        status.error("❌ Research failed - no sources found")
        return {
            "report": "# Error\n\nNo sources found for this query.",
            "scores": "No claims to score.",
            "contradictions": "No data to check.",
            "source_quality": "No sources to rate."
        }

    with iteration_log:
        st.success(f"✅ {len(queries)} searches completed simultaneously")

    status.info("📝 Synthesizing all findings...")

    # Generate report
    final_report = generate_final_report(question, all_sources)

    # Score claims
    scored = score_report(final_report, all_sources)

    # Detect contradictions
    contradictions = check_contradictions(final_report, all_sources)

    # Source quality
    source_quality = score_all_sources(all_sources)

    status.success("✅ Research complete!")

    return {
        "report": final_report,
        "scores": scored,
        "contradictions": contradictions,
        "source_quality": source_quality
    }

def run_agent(question, max_iterations=4):
    """Terminal version for testing"""
    print(f"\n📋 Research Question: {question}")
    print("=" * 60)

    all_sources = ""
    iteration = 0
    current_query = question

    while iteration < max_iterations:
        iteration += 1
        print(f"\n🔄 Iteration {iteration} of {max_iterations}")

        results = search(current_query)
        if not results:
            print("⚠️ No results found, stopping")
            break
            
        new_sources = format_sources(results)
        all_sources += new_sources

        analysis = analyze(question, all_sources)
        print("\n📊 Analysis:")
        print(analysis)

        if "NEXT_SEARCH:\nNONE" in analysis or "NEXT_SEARCH: NONE" in analysis:
            print("\n✅ Claude is satisfied. Generating final report...")
            break

        try:
            next_query = analysis.split("NEXT_SEARCH:")[1].strip()
            if not next_query or next_query.upper() == "NONE":
                break
            current_query = next_query
            print(f"\n➡️ Claude wants to search next: {current_query}")
        except:
            break

    final_report = generate_final_report(question, all_sources)
    print("\n" + "=" * 60)
    print("📄 FINAL REPORT")
    print("=" * 60)
    print(final_report)

    scored = score_report(final_report, all_sources)
    print("\n" + "=" * 60)
    print("🎯 CONFIDENCE SCORES")
    print("=" * 60)
    print(scored)

    contradictions = check_contradictions(final_report, all_sources)
    print("\n" + "=" * 60)
    print("⚠️ CONTRADICTION DETECTION")
    print("=" * 60)
    print(contradictions)

    source_quality = score_all_sources(all_sources)
    print("\n" + "=" * 60)
    print("🌐 SOURCE QUALITY")
    print("=" * 60)
    print(source_quality)