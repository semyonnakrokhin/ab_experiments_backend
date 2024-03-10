from typing import Callable

import pytest


@pytest.mark.usefixtures("conduct_experiments")
@pytest.mark.usefixtures("celery_session_app")
@pytest.mark.usefixtures("celery_session_worker")
class TestExperiments:
    def test_color_experiment_order(self, conduct_experiments: Callable):
        colors_distribution = {"#FF0000": 0, "#00FF00": 0, "#0000FF": 0}

        for _ in range(9):
            experiments = conduct_experiments()
            color = experiments[0].option.value
            colors_distribution[color] += 1

        assert colors_distribution == {"#FF0000": 3, "#00FF00": 3, "#0000FF": 3}

    def test_price_experiment_count(self, conduct_experiments: Callable):
        prices_counts = {5: 0, 10: 0, 20: 0, 50: 0}

        for _ in range(20):
            experiments = conduct_experiments()
            price = experiments[1].option.value
            prices_counts[price] += 1

        assert prices_counts == {5: 2, 10: 15, 20: 2, 50: 1}
