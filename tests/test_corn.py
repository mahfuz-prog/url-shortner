from unittest.mock import patch, MagicMock
from app.background_tasks import sync_click_corn


def test_main_success(capfd):
    # Mock DB session
    mock_db = MagicMock()

    # Patch SessionLocal to return mock_db
    with patch(
        "app.background_tasks.sync_click_corn.SessionLocal", return_value=mock_db
    ):
        # Patch sync_clicks_to_db so it doesn't actually run
        with patch(
            "app.background_tasks.sync_click_corn.sync_clicks_to_db"
        ) as mock_task:
            mock_task.return_value = None

            sync_click_corn.main()

            # Ensure sync function was called with mock db
            mock_task.assert_called_once_with(mock_db)

            # Capture stdout
            out, _ = capfd.readouterr()
            assert "Clicks synced successfully" in out


def test_main_failure(capfd):
    mock_db = MagicMock()

    with patch(
        "app.background_tasks.sync_click_corn.SessionLocal", return_value=mock_db
    ):
        with patch(
            "app.background_tasks.sync_click_corn.sync_clicks_to_db",
            side_effect=Exception,
        ):
            sync_click_corn.main()

            out, _ = capfd.readouterr()
            assert "Failed to sync clicks" in out
