from alert_dialog import AlertDialog


def test_alert_dialog():
    title = 'test title'
    alert_dialog = AlertDialog(title, 'test text')
    assert alert_dialog.__pt_container__().title == title
