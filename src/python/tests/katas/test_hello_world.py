from katas.hello_world import hello

def test_hello_world_output(capsys):
    hello()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World!"

