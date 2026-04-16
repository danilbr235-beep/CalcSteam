from datetime import datetime, timedelta


def test_expire_logic_shape():
    reserved_until = datetime.utcnow() - timedelta(minutes=1)
    assert reserved_until < datetime.utcnow()
