from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise
from typing import Any, Dict, List

import pytest
from dependency_injector.containers import DeclarativeContainer

from apps.src.database import DatabaseManager
from apps.src.db_service.exceptions import InvalidParamsError, SessionNotSetError
from apps.src.db_service.repositories import ExperimentRepository
from apps.src.schemas import ColorOptions, ExperimentsDomain, PriceOptions
from apps.src.utils import generate_device_token


@pytest.mark.usefixtures("empty_database")
class TestRepositoryInsertOne:
    @pytest.mark.parametrize(
        argnames="domain_input, expectation",
        argvalues=[
            (
                ExperimentsDomain(
                    device_token=generate_device_token(),
                    button_color=ColorOptions.RED,
                    price=PriceOptions.TEN,
                ),
                does_not_raise(),
            ),
        ],
    )
    async def test_insert_one_success(
        self,
        domain_input: ExperimentsDomain,
        database_test: DatabaseManager,
        expectation: AbstractContextManager,
        container: DeclarativeContainer,
    ):
        repository: ExperimentRepository = (
            container.repositories.experiment_repository_provider()
        )

        with expectation:
            async with database_test.get_session_factory() as session:
                repository.set_session(session)

                domain_output = await repository.insert_one(data=domain_input)

        repository.clear_session()

        assert domain_output == domain_input

    @pytest.mark.parametrize(
        argnames="domain_input, expectation",
        argvalues=[
            (
                ExperimentsDomain(
                    device_token=generate_device_token(),
                    button_color=ColorOptions.RED,
                    price=PriceOptions.TEN,
                ),
                pytest.raises(SessionNotSetError),
            ),
        ],
    )
    async def test_insert_one_errors(
        self,
        domain_input: ExperimentsDomain,
        database_test: DatabaseManager,
        expectation: AbstractContextManager,
        container: DeclarativeContainer,
    ):
        repository: ExperimentRepository = (
            container.repositories.experiment_repository_provider()
        )

        with expectation:
            async with database_test.get_session_factory():
                await repository.insert_one(data=domain_input)


@pytest.mark.usefixtures("empty_database")
class TestSelectSomeByParams:
    @pytest.mark.parametrize(
        argnames="params, expectation",
        argvalues=[
            ({"device_token": generate_device_token()}, does_not_raise()),
            (
                {"device_token": generate_device_token(), "lalala": "test_data"},
                pytest.raises(InvalidParamsError),
            ),
            (
                {
                    "device_token": generate_device_token(),
                    "button_color": "#FF0000",
                    "price": 10,
                },
                does_not_raise(),
            ),
            ([1, 2, 3], pytest.raises(TypeError)),
        ],
    )
    async def test_select_some_with_different_params(
        self,
        params: Dict[str, Any],
        database_test: DatabaseManager,
        expectation: AbstractContextManager,
        container: DeclarativeContainer,
    ):
        try:
            device_token = (
                params.get("device_token")
                if params.get("device_token")
                else generate_device_token()
            )
        except Exception:
            device_token = generate_device_token()

        test_experiment = ExperimentsDomain(
            device_token=device_token,
            button_color=ColorOptions.RED,
            price=PriceOptions.TEN,
        )

        repository: ExperimentRepository = (
            container.repositories.experiment_repository_provider()
        )

        with expectation:
            async with database_test.get_session_factory() as session:
                repository.set_session(session)
                await repository.insert_one(data=test_experiment)
                domains_output_lst = await repository.select_some_by_params(
                    params=params
                )

            domain_output = domains_output_lst[0]
            assert domain_output == test_experiment

        repository.clear_session()


@pytest.mark.usefixtures("insert_data_to_database")
class TestSelectAggregated:
    @pytest.mark.parametrize(
        argnames="expected_output, expectation",
        argvalues=[
            (
                [
                    {
                        "experiment_name": "button_color",
                        "data": [
                            ("#FF0000", 7, 20, 35.0),
                            ("#00FF00", 7, 20, 35.0),
                            ("#0000FF", 6, 20, 30.0),
                        ],
                    },
                    {
                        "experiment_name": "price",
                        "data": [
                            (50, 1, 20, 5.0),
                            (20, 2, 20, 10.0),
                            (10, 15, 20, 75.0),
                            (5, 2, 20, 10.0),
                        ],
                    },
                ],
                does_not_raise(),
            ),
        ],
    )
    async def test_select_some_with_different_params(
        self,
        database_test: DatabaseManager,
        container: DeclarativeContainer,
        expected_output: List[Dict],
        expectation: AbstractContextManager,
    ):
        repository: ExperimentRepository = (
            container.repositories.experiment_repository_provider()
        )

        with expectation:
            async with database_test.get_session_factory() as session:
                repository.set_session(session)
                result_lst = await repository.select_aggregated()

            assert result_lst == expected_output

        repository.clear_session()
