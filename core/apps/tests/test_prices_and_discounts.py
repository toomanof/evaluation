import pytest
from icecream import ic

from core.apps.basic.services.handlers.prices_and_discounts import PricesAndDiscountsHandler
from core.project.utils import time_of_completion
from core.apps.basic.types.types import SupplierTaskMetadataBuffer
from core.project.types import MsgResponseToPlatform
from core.apps.basic.types.responses import (
    WBResponseObjectDownloadProcessedStatus,
    WBResponseObjectProcessedLoadDetail,
)


@pytest.mark.asyncio
@time_of_completion
async def test_positive_export_prices_and_discounts(app, body_request_export_price_and_discounts) -> None:
    handler = PricesAndDiscountsHandler(
        app=app,
        body=body_request_export_price_and_discounts,
        # test=True
    )
    result = await handler.export_price_and_discounts()
    ic(result)
    ic(result.data)
    assert len(result.data) > 0


@pytest.mark.asyncio
@time_of_completion
async def test_positive_download_processed_status(app, body_request_download_processed_status) -> None:
    handler = PricesAndDiscountsHandler(
        app=app,
        body=body_request_download_processed_status,
    )
    result = await handler.download_processed_status()
    ic(result)
    assert isinstance(result.data.data, WBResponseObjectDownloadProcessedStatus)


@pytest.mark.asyncio
@time_of_completion
async def test_positive_processed_load_details(app, body_request_processed_load_details) -> None:
    handler = PricesAndDiscountsHandler(
        app=app,
        body=body_request_processed_load_details,
    )
    result = await handler.processed_load_details()
    ic(result)
    assert isinstance(result.data.data, WBResponseObjectProcessedLoadDetail)


@pytest.mark.asyncio
@time_of_completion
async def test_positive_raw_load_detail(app, body_request_processed_load_details) -> None:
    handler = PricesAndDiscountsHandler(
        app=app,
        body=body_request_processed_load_details,
    )
    result = await handler.raw_load_detail()
    ic(result)
    assert isinstance(result.data.data, WBResponseObjectProcessedLoadDetail)


@pytest.mark.asyncio
@time_of_completion
async def test_positive_raw_load_progress(app, body_request_load_progress) -> None:
    handler = PricesAndDiscountsHandler(
        app=app,
        body=body_request_load_progress,
    )
    result = await handler.raw_load_progress()
    ic(result)
    assert isinstance(result.data.data, SupplierTaskMetadataBuffer)


@pytest.mark.asyncio
@time_of_completion
async def test_positive_raw_load_progress_500_status(
    app, body_request_load_progress, initiate_500_status_headers
) -> None:
    body = body_request_load_progress.copy()
    body.headers = initiate_500_status_headers
    handler = PricesAndDiscountsHandler(
        app=app,
        body=body,
    )
    result = await handler.raw_load_progress()
    ic(result)
    assert isinstance(result, MsgResponseToPlatform)
    # assert isinstance(result.data, MsgResponseToPlatform)
