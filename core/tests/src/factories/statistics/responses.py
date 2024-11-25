from core.apps.basic.types.responses import WBFBOOrder
from core.apps.basic.types.types import WBSales, WBSalesReportItem
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory import Use
import uuid
from core.tests.src.factories import TEST_PRODUCTS_IDS_RANGE


class WBFBOOrderFactory(ModelFactory[WBFBOOrder]):
    warehouseName = "Подольск"
    countryName = "Россия"
    oblastOkrugName = "Центральный федеральный округ"
    regionName = "Московская"
    supplierArticle = "12345"
    nmId = lambda: ModelFactory.__random__.choice(TEST_PRODUCTS_IDS_RANGE)
    barcode = "123453559000"
    category = "Бытовая техника"
    subject = "Мультистайлеры"
    brand = "Тест"
    techSize = "0"
    incomeID = Use(ModelFactory.__random__.randint, 1, 10000)
    totalPrice = Use(ModelFactory.__random__.randint, 1, 10000)
    discountPercent = Use(ModelFactory.__random__.randint, 1, 20)
    spp = Use(ModelFactory.__random__.randint, 1, 20)
    finishedPrice = Use(ModelFactory.__random__.randint, 1, 10000)
    priceWithDisc = Use(ModelFactory.__random__.randint, 1, 10000)
    orderType = "Клиентский"
    sticker = "926912515"
    gNumber = str(uuid.uuid4())
    srid = str(uuid.uuid4())
    all_products_matched_to_platform = False


class WBSalesFactory(ModelFactory[WBSales]):
    warehouseName = "Подольск"
    countryName = "Россия"
    oblastOkrugName = "Центральный федеральный округ"
    regionName = "Московская"
    supplierArticle = "12345"
    nmId = Use(ModelFactory.__random__.randint, 1, 10000)
    barcode = "123453559000"
    category = "Бытовая техника"
    subject = "Мультистайлеры"
    brand = "Тест"
    techSize = "0"
    incomeID = Use(ModelFactory.__random__.randint, 1, 10000)
    totalPrice = Use(ModelFactory.__random__.uniform, 1, 10000)
    discountPercent = Use(ModelFactory.__random__.randint, 1, 20)
    spp = Use(ModelFactory.__random__.uniform, 1, 20)
    paymentSaleAmount = Use(ModelFactory.__random__.randint, 1, 5000)
    forPay = Use(ModelFactory.__random__.uniform, 1, 5000)
    finishedPrice = Use(ModelFactory.__random__.uniform, 1, 10000)
    priceWithDisc = Use(ModelFactory.__random__.uniform, 1, 10000)
    saleID = "S9993700024"
    orderType = "Клиентский"
    sticker = "926912515"
    gNumber = str(uuid.uuid4())
    srid = str(uuid.uuid4())


class WBSalesReportFactory(ModelFactory[WBSalesReportItem]):
    realizationreport_id = Use(ModelFactory.__random__.randint, 1, 1000000)
    date_from = "2024-09-30"
    date_to = "2024-10-06"
    create_dt = "2024-10-07"
    currency_name = "RUB"
    suppliercontract_code = None
    rrd_id = Use(ModelFactory.__random__.randint, 1, 1000000)
    gi_id = Use(ModelFactory.__random__.randint, 1, 100000)
    dlv_prc = Use(ModelFactory.__random__.randint, 1, 100000)
    fix_tariff_date_from = ""
    fix_tariff_date_to = ""
    subject_name = "Аксессуары для банных печей"
    nm_id = Use(ModelFactory.__random__.randint, 1, 100000)
    brand_name = "Бежецкое литье"
    sa_name = "колосник-бежецк-ру-2"
    ts_name = "0"
    barcode = "4615069225392"
    doc_type_name = ""
    quantity = Use(ModelFactory.__random__.randint, 1, 1000)
    retail_price = Use(ModelFactory.__random__.randint, 1, 100000)
    retail_amount = Use(ModelFactory.__random__.randint, 1, 100000)
    sale_percent = Use(ModelFactory.__random__.randint, 1, 10000)
    commission_percent = Use(ModelFactory.__random__.randint, 1, 10000)
    office_name = "Склад поставщика - везу на склад WB"
    supplier_oper_name = "Логистика"
    order_dt = "2024-09-28T18:03:02Z"
    sale_dt = "2024-10-03T08:27:52Z"
    rr_dt = "2024-10-03"
    shk_id = Use(ModelFactory.__random__.randint, 1, 1000000)
    retail_price_withdisc_rub = 0
    delivery_amount = 1
    return_amount = 0
    delivery_rub = 44
    gi_box_type_name = ""
    product_discount_for_report = 0
    supplier_promo = 0
    rid = 0
    ppvz_spp_prc = 0
    ppvz_kvw_prc_base = 0
    ppvz_kvw_prc = 0
    sup_rating_prc_up = 0
    is_kgvp_v2 = 0
    ppvz_sales_commission = 0
    ppvz_for_pay = 0
    ppvz_reward = 0
    acquiring_fee = 0
    acquiring_percent = 0
    payment_processing = ""
    acquiring_bank = ""
    ppvz_vw = 0
    ppvz_vw_nds = 0
    ppvz_office_name = ""
    ppvz_office_id = 217885
    ppvz_supplier_id = 0
    ppvz_supplier_name = ""
    ppvz_inn = ""
    declaration_number = ""
    bonus_type_name = "К клиенту при продаже"
    sticker_id = "24803947932"
    site_country = "Беларусь"
    srv_dbs = False
    penalty = 0
    additional_payment = 0
    rebill_logistic_cost = 0
    storage_fee = 0
    deduction = 0
    acceptance = 0
    assembly_id: 2231170692
    srid = "dm.r500a4618e5b54d3e964bdcd0dc83a0f9.0.0"
    report_type = 2
