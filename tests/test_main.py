from flatsearch.main import main


def test_main():
    assert main("foo") is True
