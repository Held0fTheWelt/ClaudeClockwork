def test_package_importable_and_versioned():
    import clockwork

    assert clockwork.__version__ == "0.1.0"
