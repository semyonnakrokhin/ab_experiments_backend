from contextlib import nullcontext as does_not_raise
from unittest import mock

import pytest

from apps.src.db_service.exceptions import (
    DatabaseError,
    MappingError,
    SessionNotSetError,
)
from apps.src.db_service.repositories import ExperimentRepository
from apps.src.schemas import ColorOptions, ExperimentsDomain, PriceOptions
from apps.src.utils import generate_device_token


@pytest.mark.usefixtures("empty_database")
class TestDatabaseServiceAdd:
    @pytest.mark.parametrize(
        argnames="domain_input, expected_output, expectation",
        argvalues=[
            (
                ExperimentsDomain(
                    device_token="02392c7d-fb6b-48a0-9edf-97edfcfdfadf",
                    button_color=ColorOptions.RED,
                    price=PriceOptions.TEN,
                ),
                ExperimentsDomain(
                    device_token="02392c7d-fb6b-48a0-9edf-97edfcfdfadf",
                    button_color=ColorOptions.RED,
                    price=PriceOptions.TEN,
                ),
                does_not_raise(),
            )
        ],
    )
    async def test_add_experiments_success(
        self, container, domain_input, expected_output, expectation
    ):
        repository_mock = mock.Mock(spec=ExperimentRepository)
        repository_mock.insert_one.return_value = expected_output

        with expectation:
            with container.repositories.experiment_repository_provider.override(
                repository_mock
            ):
                service = container.services.database_service_provider()
                result = await service.add_experiments(experiments=domain_input)

            assert result == expected_output

    @pytest.mark.parametrize(
        argnames="error_type",
        argvalues=[
            SessionNotSetError,
            MappingError,
            DatabaseError,
            AttributeError,
        ],
    )
    async def test_add_file_raising_errors(self, container, error_type):
        repository_mock = mock.Mock(spec=ExperimentRepository)
        repository_mock.insert_one.side_effect = error_type("Mocked error")

        test_experiment = ExperimentsDomain(
            device_token=generate_device_token(),
            button_color=ColorOptions.RED,
            price=PriceOptions.TEN,
        )

        with container.repositories.experiment_repository_provider.override(
            repository_mock
        ):
            service = container.services.database_service_provider()

            with pytest.raises(error_type):
                await service.add_experiments(experiments=test_experiment)


class TestDatabaseServiceGetByToken:
    @pytest.mark.parametrize(
        argnames="device_token, expectation",
        argvalues=[(generate_device_token(), does_not_raise())],
    )
    async def test_get_experiments_success(
        self, container, device_token, expectation, database_test
    ):
        test_experiment = ExperimentsDomain(
            device_token=device_token,
            button_color=ColorOptions.RED,
            price=PriceOptions.TEN,
        )

        repository_mock = mock.Mock(spec=ExperimentRepository)
        repository_mock.select_some_by_params.return_value = [test_experiment]

        with expectation:
            with container.repositories.experiment_repository_provider.override(
                repository_mock
            ):
                service = container.services.database_service_provider()
                result = await service.get_experiments_by_device_token(
                    device_token=device_token
                )

            assert result == test_experiment

    @pytest.mark.parametrize(
        argnames="error_type",
        argvalues=[
            SessionNotSetError,
            MappingError,
            DatabaseError,
            AttributeError,
            TypeError,
        ],
    )
    async def test_add_file_raising_errors(self, container, error_type):
        repository_mock = mock.Mock(spec=ExperimentRepository)
        repository_mock.select_some_by_params.side_effect = error_type("Mocked error")

        device_token = generate_device_token()

        with container.repositories.experiment_repository_provider.override(
            repository_mock
        ):
            service = container.services.database_service_provider()

            with pytest.raises(error_type):
                await service.get_experiments_by_device_token(device_token=device_token)


@pytest.mark.usefixtures("insert_data_to_database")
class TestDatabaseServiceGetStatistics:
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
    async def test_get_statistics_success(
        self, container, expected_output, expectation
    ):
        repository_mock = mock.Mock(spec=ExperimentRepository)
        repository_mock.select_aggregated.return_value = expected_output

        with expectation:
            with container.repositories.experiment_repository_provider.override(
                repository_mock
            ):
                service = container.services.database_service_provider()
                result = await service.get_statistics_on_all_experiments()

            assert result == expected_output

    @pytest.mark.parametrize(
        argnames="error_type",
        argvalues=[SessionNotSetError, DatabaseError, AttributeError],
    )
    async def test_add_file_raising_errors(self, container, error_type):
        repository_mock = mock.Mock(spec=ExperimentRepository)
        repository_mock.select_aggregated.side_effect = error_type("Mocked error")

        with container.repositories.experiment_repository_provider.override(
            repository_mock
        ):
            service = container.services.database_service_provider()

            with pytest.raises(error_type):
                await service.get_statistics_on_all_experiments()
