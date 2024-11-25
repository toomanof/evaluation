import pytest

from core.apps.basic.services.handlers import CommonHandler


@pytest.mark.asyncio
@pytest.mark.separate_test_session
async def test_positive_import_stock(running_app, body_request_import_stock) -> None:
    handler = CommonHandler(app=running_app, body=body_request_import_stock)
    result = await handler.import_stock()
    assert len(result.data) > 0
    assert len(result.errors) == 0


@pytest.mark.asyncio
async def test_positive_import_stock_fbo(running_app, body_request_import_stock_fbo) -> None:
    handler = CommonHandler(app=running_app, body=body_request_import_stock_fbo)
    result = await handler.import_stock_fbo()
    assert len(result.data) > 0
    assert len(result.errors) == 0


@pytest.mark.asyncio
async def test_positive_export_stock(running_app, body_request_export_stock) -> None:
    handler = CommonHandler(app=running_app, body=body_request_export_stock)
    result = await handler.export_stock()
    assert isinstance(result.data, bool) and result.data is True
    assert len(result.errors) == 0
