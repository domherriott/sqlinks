from sqlinks.app import scan as scan


def test_scan_count():
    assert len(scan.main(".")) == 2
