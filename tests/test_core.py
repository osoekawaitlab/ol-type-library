from oltl import core


def test_id_generates_inherited_class_instance() -> None:
    class MyId(core.Id):
        pass

    actual = MyId.generate()
    assert isinstance(actual, MyId)
    assert isinstance(actual, core.Id)
