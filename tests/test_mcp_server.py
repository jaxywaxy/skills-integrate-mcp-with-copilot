from src.mcp_server import list_activities, search_activities, signup_for_activity, unregister_from_activity


def test_list_activities_returns_activity_overview():
    activities = list_activities()

    assert "Chess Club" in activities
    assert "description" in activities["Chess Club"]
    assert "spots_left" in activities["Chess Club"]


def test_signup_and_unregister_work_for_activity():
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    try:
        result = signup_for_activity(activity, email)
        assert result["message"] == f"Signed up {email} for {activity}"
        assert email in list_activities()[activity]["participants"]

        result = unregister_from_activity(activity, email)
        assert result["message"] == f"Unregistered {email} from {activity}"
        assert email not in list_activities()[activity]["participants"]
    finally:
        try:
            unregister_from_activity(activity, email)
        except Exception:
            pass


def test_search_activities_filters_by_name_and_keyword():
    results = search_activities("soccer")
    assert any("Soccer Team" == item["name"] for item in results)

    results = search_activities("arts")
    assert any("Art Club" == item["name"] for item in results)
