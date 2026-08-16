from unittest.mock import Mock


def test_versand():
    mailer = Mock()
    mailer.send("a")
    mailer.send.assert_called_once()   # !! TEST_MOCK_CALL
