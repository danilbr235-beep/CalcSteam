from app.services.pricing_service import ComboEval


def test_combo_ranking_priority():
    rows = [
        ComboEval([1], 20, 100, 1, 2, 300, 50, 1, True),
        ComboEval([1, 2], 20, 110, 1, 2, 300, 50, 0.5, True),
        ComboEval([3], 20, 120, 1, 2, 300, 60, 5, True),
    ]
    best = sorted(rows, key=lambda x: (-x.expected_net_profit, len(x.code_ids), x.deviation_percent))[0]
    assert best.code_ids == [3]
