"""
AI router — natural language querying and plain-language annotation of regulations.
Uses Claude claude-opus-4-6 with adaptive thinking, streaming, and prompt caching.
"""
from __future__ import annotations

import os
import logging
from typing import List, Optional

import anthropic
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..database import get_db, row_to_dict

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])

VALID_VERTICALS = {"crypto", "fintech", "healthcare", "insurance", "saas"}

MODEL = "claude-opus-4-6"

SYSTEM_PROMPT = """You are LATTICE, an expert regulatory compliance analyst. You have deep knowledge of financial services regulation, healthcare compliance, cryptocurrency regulation, insurance law, and SaaS data privacy requirements.

When answering questions about regulations:
- Be precise and cite specific regulation IDs and titles when relevant
- Explain compliance requirements in plain, actionable language
- Flag critical deadlines and high-impact items
- Structure your response with clear sections when the question is complex
- If asked about a specific regulation, focus on practical compliance implications"""

ANNOTATION_PROMPT = """You are a regulatory compliance expert. Analyze the following regulation and produce a clear, structured plain-language explanation suitable for compliance teams and business leaders.

Your annotation must include:
1. **What this regulation requires** — the core obligations in plain language
2. **Who is affected** — which businesses and entities must comply
3. **Key deadlines** — any compliance deadlines or effective dates
4. **Practical steps** — 3-5 concrete actions to achieve compliance
5. **Risk of non-compliance** — potential penalties or consequences
6. **Plain-language summary** — one paragraph suitable for non-lawyers

Be concise, practical, and clear. Avoid legal jargon where possible."""


def _get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(500, "ANTHROPIC_API_KEY not configured")
    return anthropic.Anthropic(api_key=api_key)


def _fetch_regulations_context(
    conn,
    vertical: Optional[str] = None,
    limit: int = 30,
) -> str:
    """Build a context string of regulations for Claude to reference."""
    if vertical and vertical in VALID_VERTICALS:
        rows = conn.execute(
            """SELECT r.regulation_id, r.title, r.status, r.summary, r.deadline_date,
                      r.impact_score, r.published_date
               FROM regulations r
               JOIN regulation_verticals rv ON r.id = rv.regulation_id
               WHERE rv.vertical = ?
               ORDER BY r.impact_score DESC LIMIT ?""",
            (vertical, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT r.regulation_id, r.title, r.status, r.summary, r.deadline_date,
                      r.impact_score, r.published_date
               FROM regulations r
               ORDER BY r.impact_score DESC LIMIT ?""",
            (limit,),
        ).fetchall()

    lines = []
    for r in rows:
        d = dict(r)
        line = f"[{d['regulation_id']}] {d['title']} | Status: {d['status']} | Impact: {d['impact_score']}/10"
        if d.get("deadline_date"):
            line += f" | Deadline: {d['deadline_date']}"
        if d.get("summary"):
            line += f"\n  Summary: {d['summary'][:300]}"
        lines.append(line)

    return "\n\n".join(lines)


# ─── Request / Response models ────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    vertical: Optional[str] = None
    stream: bool = True


class AnnotationResponse(BaseModel):
    regulation_id: str
    title: str
    annotation: str
    cached: bool
    model_used: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/query")
def ai_query(req: QueryRequest):
    """
    Natural language query over the regulation database.
    Streams Claude's response if req.stream=True (default).
    """
    if req.vertical and req.vertical not in VALID_VERTICALS:
        raise HTTPException(400, f"Invalid vertical. Valid: {sorted(VALID_VERTICALS)}")

    with get_db() as conn:
        context = _fetch_regulations_context(conn, req.vertical)

    client = _get_client()

    user_message = f"""I have a question about regulatory compliance. Here is the current set of tracked regulations for context:

<regulations>
{context}
</regulations>

My question: {req.question}"""

    if req.stream:
        def generate():
            with client.messages.stream(
                model=MODEL,
                max_tokens=2048,
                thinking={"type": "adaptive"},
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": user_message}],
            ) as stream:
                for text in stream.text_stream:
                    yield text

        return StreamingResponse(generate(), media_type="text/plain")
    else:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_message}],
        )
        text = next(
            (b.text for b in response.content if b.type == "text"), ""
        )
        return {"answer": text, "model": MODEL}


def _generate_annotation(client: anthropic.Anthropic, reg: dict) -> str:
    reg_text = f"""Regulation ID: {reg['regulation_id']}
Title: {reg['title']}
Type: {reg.get('type', 'N/A')}
Status: {reg.get('status', 'N/A')}
Source: {reg.get('source', 'N/A')}
Published: {reg.get('published_date', 'N/A')}
Effective Date: {reg.get('effective_date', 'N/A')}
Deadline: {reg.get('deadline_date', 'N/A')}
Impact Score: {reg.get('impact_score', 'N/A')}/10
Complexity Score: {reg.get('complexity_score', 'N/A')}/10
Citation: {reg.get('citation', 'N/A')}

Summary:
{reg.get('summary') or reg.get('title')}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        thinking={"type": "adaptive"},
        system=ANNOTATION_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Please provide a plain-language annotation for this regulation:\n\n{reg_text}",
            }
        ],
    )

    return next((b.text for b in response.content if b.type == "text"), "")


@router.post("/annotate/{regulation_id_slug}", response_model=AnnotationResponse)
def annotate_regulation(regulation_id_slug: str, force_refresh: bool = Query(False)):
    """
    Generate a plain-language AI annotation for a specific regulation.
    Result is cached in the database; use force_refresh=true to regenerate.
    """
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM regulations WHERE regulation_id=?", (regulation_id_slug,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Regulation not found")

        reg = row_to_dict(row)

        # Check cache
        if not force_refresh:
            cached = conn.execute(
                "SELECT annotation, model_used FROM regulation_annotations WHERE regulation_id=?",
                (reg["id"],),
            ).fetchone()
            if cached:
                return AnnotationResponse(
                    regulation_id=regulation_id_slug,
                    title=reg["title"],
                    annotation=cached[0],
                    cached=True,
                    model_used=cached[1] or MODEL,
                )

    client = _get_client()
    annotation_text = _generate_annotation(client, reg)

    # Cache the result
    with get_db() as conn:
        conn.execute(
            """INSERT INTO regulation_annotations (regulation_id, annotation, model_used)
               VALUES (?, ?, ?)
               ON CONFLICT(regulation_id) DO UPDATE SET
                 annotation=excluded.annotation,
                 model_used=excluded.model_used,
                 updated_at=CURRENT_TIMESTAMP""",
            (reg["id"], annotation_text, MODEL),
        )
        conn.commit()

    return AnnotationResponse(
        regulation_id=regulation_id_slug,
        title=reg["title"],
        annotation=annotation_text,
        cached=False,
        model_used=MODEL,
    )


@router.get("/annotation/{regulation_id_slug}", response_model=AnnotationResponse)
def get_annotation(regulation_id_slug: str):
    """Retrieve a cached AI annotation for a regulation, if one exists."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM regulations WHERE regulation_id=?", (regulation_id_slug,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Regulation not found")

        reg = row_to_dict(row)
        cached = conn.execute(
            "SELECT annotation, model_used FROM regulation_annotations WHERE regulation_id=?",
            (reg["id"],),
        ).fetchone()

    if not cached:
        raise HTTPException(404, "No annotation yet — call POST /ai/annotate/{id} to generate one")

    return AnnotationResponse(
        regulation_id=regulation_id_slug,
        title=reg["title"],
        annotation=cached[0],
        cached=True,
        model_used=cached[1] or MODEL,
    )
