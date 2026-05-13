def test_notify_task_finished(client):
    response = client.post("/notify", json={
        "event": "task.finished",
        "task_id": "abc123",
        "user_id": "user1",
        "title": "Buy groceries",
    })
    assert response.status_code == 202
    data = response.json()
    assert data["accepted"] is True
    assert data["event"] == "task.finished"
    assert "notification_id" in data


def test_notify_all_event_types(client):
    for event in ["task.finished", "task.cancelled", "task.created", "task.deferred"]:
        response = client.post("/notify", json={
            "event": event,
            "task_id": "abc123",
            "user_id": "user1",
            "title": "Test task",
        })
        assert response.status_code == 202, f"Failed for event: {event}"


def test_notify_unknown_event_rejected(client):
    response = client.post("/notify", json={
        "event": "task.unknown",
        "task_id": "abc123",
        "user_id": "user1",
        "title": "Test task",
    })
    assert response.status_code == 422


def test_notify_missing_task_id_rejected(client):
    response = client.post("/notify", json={
        "event": "task.finished",
        "user_id": "user1",
        "title": "Test task",
    })
    assert response.status_code == 422


def test_notify_missing_user_id_rejected(client):
    response = client.post("/notify", json={
        "event": "task.finished",
        "task_id": "abc123",
        "title": "Test task",
    })
    assert response.status_code == 422


def test_notify_with_extra_data(client):
    response = client.post("/notify", json={
        "event": "task.finished",
        "task_id": "abc123",
        "user_id": "user1",
        "title": "Buy groceries",
        "data": {"completion_note": "All done", "priority": "high"},
    })
    assert response.status_code == 202


def test_dispatcher_is_called(client, mock_dispatcher):
    client.post("/notify", json={
        "event": "task.finished",
        "task_id": "abc123",
        "user_id": "user1",
        "title": "Buy groceries",
    })
    mock_dispatcher.dispatch.assert_called_once()
    call_arg = mock_dispatcher.dispatch.call_args[0][0]
    assert call_arg.event.value == "task.finished"
    assert call_arg.task_id == "abc123"
    assert call_arg.user_id == "user1"


def test_dispatcher_result_returned(client, mock_dispatcher):
    response = client.post("/notify", json={
        "event": "task.finished",
        "task_id": "abc123",
        "user_id": "user1",
        "title": "Buy groceries",
    })
    assert response.json()["notification_id"] == "test-notification-id"
