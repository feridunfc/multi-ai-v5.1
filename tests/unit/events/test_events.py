from multi_ai.events.schemas import GitHubWebhookEvent, EventType

def test_github_webhook_event_defaults():
    ev = GitHubWebhookEvent(
        source="test",
        github_event_name="pull_request",
        github_delivery_id="1",
        repository_full_name="owner/repo",
        payload={},
    )
    assert ev.event_type == EventType.GITHUB_WEBHOOK
