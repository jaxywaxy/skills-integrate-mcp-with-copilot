"""MCP server for managing extracurricular activities."""

from __future__ import annotations

import re

from mcp.server.fastmcp import FastMCP

from src.app import activities


def _normalize_search_text(value: str) -> str:
    """Normalize text for flexible keyword matching."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    words = []
    for word in value.split():
        if word.endswith("ies") and len(word) > 3:
            word = word[:-3] + "y"
        elif word.endswith("sses") and len(word) > 4:
            word = word[:-2]
        elif word.endswith("es") and len(word) > 3 and not word.endswith(("ses", "xes", "zes", "ches", "shes")):
            word = word[:-2]
        elif word.endswith("s") and len(word) > 3 and not word.endswith("ss"):
            word = word[:-1]
        words.append(word)
    return " ".join(words)

mcp = FastMCP("Mergington High School Activities")


@mcp.tool()
def list_activities() -> dict[str, dict[str, object]]:
    """Return the current list of activities and their details."""
    result = {}
    for name, details in activities.items():
        result[name] = {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "spots_left": details["max_participants"] - len(details["participants"]),
            "participants": details["participants"],
        }
    return result


@mcp.tool()
def search_activities(query: str) -> list[dict[str, str | int | list[str]]]:
    """Find activities whose name or description matches a query."""
    normalized_query = _normalize_search_text(query)
    if not normalized_query:
        return []

    matches = []
    for name, details in activities.items():
        haystack = _normalize_search_text(f"{name} {details['description']}")
        if normalized_query in haystack:
            matches.append({
                "name": name,
                "description": details["description"],
                "schedule": details["schedule"],
                "spots_left": details["max_participants"] - len(details["participants"]),
                "participants": details["participants"],
            })
    return matches


@mcp.tool()
def signup_for_activity(activity_name: str, email: str) -> dict[str, str]:
    """Register a student for an activity or raise an error if invalid."""
    if activity_name not in activities:
        raise ValueError(f"Activity '{activity_name}' not found")

    activity = activities[activity_name]
    if email in activity["participants"]:
        raise ValueError(f"Student is already signed up for {activity_name}")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise ValueError(f"Activity '{activity_name}' is full")

    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@mcp.tool()
def unregister_from_activity(activity_name: str, email: str) -> dict[str, str]:
    """Remove a student from an activity if they are currently enrolled."""
    if activity_name not in activities:
        raise ValueError(f"Activity '{activity_name}' not found")

    activity = activities[activity_name]
    if email not in activity["participants"]:
        raise ValueError(f"Student is not signed up for {activity_name}")

    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


if __name__ == "__main__":
    mcp.run()
