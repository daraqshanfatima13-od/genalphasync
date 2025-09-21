from crisis_detector import check_crisis
def test_simple_crisis():
    assert check_crisis("I want to kill myself")["crisis"] == True
def test_non_crisis():
    assert check_crisis("I am so happy")["crisis"] == False
