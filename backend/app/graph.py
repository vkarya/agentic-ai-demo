"""LangGraph workflow for feedback summarization and sentiment analysis."""

from __future__ import annotations

import json
from typing import Any, Dict

from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from .config import get_settings
from .schemas import FeedbackAnalysisResponse, SentimentType


class FeedbackState(TypedDict, total=False):
    """State shared across the LangGraph workflow."""

    feedback_text: str
    summary: str
    sentiment: SentimentType
    reason: str
    sentiment_tool_result: Dict[str, Any]


settings = get_settings()

llm = ChatOpenAI(
    base_url=settings.llm_api_base,
    api_key=settings.llm_api_key,
    model=settings.llm_model,
)


def summarize_node(state: FeedbackState) -> FeedbackState:
    """Summarizer agent: produce a concise neutral summary of the feedback."""
    feedback_text = state.get("feedback_text", "")
    if not feedback_text:
        return state

    system_prompt = (
        "You are a helpful assistant that summarizes customer feedback. "
        "Provide a concise, neutral summary in 1-3 sentences without adding opinions."
    )
    user_prompt = f"Customer feedback:\n\n{feedback_text}\n\nSummary:"

    response = llm.invoke(
        [
            ("system", system_prompt),
            ("user", user_prompt),
        ]
    )

    summary_text = response.content.strip() if hasattr(response, "content") else str(response)
    return {
        **state,
        "summary": summary_text,
    }


def _run_sentiment_tool(summary: str) -> Dict[str, Any]:
    """Very simple keyword-based sentiment tool over the summary text."""
    text = summary.lower()

    positive_keywords = [
        "good",
        "great",
        "excellent",
        "happy",
        "satisfied",
        "love",
        "amazing",
        "fantastic",
        "awesome",
    ]
    negative_keywords = [
        "bad",
        "terrible",
        "awful",
        "unhappy",
        "angry",
        "disappointed",
        "hate",
        "frustrated",
        "poor",
    ]

    positive_hits = [kw for kw in positive_keywords if kw in text]
    negative_hits = [kw for kw in negative_keywords if kw in text]

    score = len(positive_hits) - len(negative_hits)
    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"
    else:
        label = "neutral"

    return {
        "label": label,
        "score": score,
        "positive_keywords_found": positive_hits,
        "negative_keywords_found": negative_hits,
    }


def sentiment_node(state: FeedbackState) -> FeedbackState:
    """Sentiment agent: call the sentiment tool and decide HAPPY or UNHAPPY."""
    summary = state.get("summary", "")
    if not summary:
        return state

    # Simple internal sentiment helper over the summary text.
    tool_result = _run_sentiment_tool(summary)

    system_prompt = (
        "You are a customer sentiment analyst.\n"
        "You receive a neutral summary of customer feedback and the output of a simple "
        "keyword-based sentiment tool.\n"
        "Decide if the customer is overall HAPPY or UNHAPPY.\n"
        "Respond strictly as compact JSON with keys 'sentiment' and 'reason'.\n"
        "The 'sentiment' value must be exactly one of: HAPPY, UNHAPPY."
    )

    user_prompt = (
        f"Summary:\n{summary}\n\n"
        f"Tool output (JSON):\n{json.dumps(tool_result)}\n\n"
        "Return JSON only, no extra text."
    )

    response = llm.invoke(
        [
            ("system", system_prompt),
            ("user", user_prompt),
        ]
    )

    raw_content = response.content if hasattr(response, "content") else str(response)

    sentiment: SentimentType = "UNHAPPY"
    reason = "Could not parse model response."

    try:
        parsed = json.loads(raw_content)
        raw_sentiment = str(parsed.get("sentiment", "")).strip().upper()
        if raw_sentiment == "HAPPY":
            sentiment = "HAPPY"
        else:
            sentiment = "UNHAPPY"

        parsed_reason = parsed.get("reason")
        if isinstance(parsed_reason, str) and parsed_reason.strip():
            reason = parsed_reason.strip()
        else:
            reason = f"Model classified customer as {sentiment} based on the summary and tool output."
    except json.JSONDecodeError:
        # Fallback: treat the entire response as a free-form explanation.
        sentiment = "UNHAPPY"
        reason = raw_content.strip() or reason

    return {
        **state,
        "sentiment": sentiment,
        "reason": reason,
        "sentiment_tool_result": tool_result,
    }


graph_builder = StateGraph(FeedbackState)
graph_builder.add_node("summarizer", summarize_node)
graph_builder.add_node("sentiment", sentiment_node)
graph_builder.set_entry_point("summarizer")
graph_builder.add_edge("summarizer", "sentiment")
graph_builder.add_edge("sentiment", END)

feedback_graph = graph_builder.compile()


def run_feedback_workflow(feedback_text: str) -> FeedbackAnalysisResponse:
    """Helper to run the full workflow and return a pydantic response model."""
    initial_state: FeedbackState = {"feedback_text": feedback_text}
    final_state = feedback_graph.invoke(initial_state)

    summary = final_state.get("summary", "") or ""
    sentiment = final_state.get("sentiment", "UNHAPPY") or "UNHAPPY"
    reason = final_state.get("reason", "") or ""

    return FeedbackAnalysisResponse(summary=summary, sentiment=sentiment, reason=reason)

