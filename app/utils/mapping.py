from flatten_dict import flatten
import logging

logger = logging.getLogger(__name__)

SELLER_NAME_MAP = {
    1: "SUNWOOD VIETNAM",
    2: "ACME EXPORT",
}

BUYER_NAME_MAP = {
    2: "KOREA BIOMASS CO., LTD.",
    3: "ABC ENERGY",
}

PLACEHOLDER_MAP = {
    'T_PURCHASE_CONTRACT.CODE': '8',
    'T_PURCHASE_CONTRACT.CONTRACT_DATE': '3',
    'T_PURCHASE_CONTRACT.PORT_OF_LOADING': '11',
    'T_PURCHASE_CONTRACT.PORT_OF_DISCHARGE': '12',
    'T_PURCHASE_CONTRACT.VESSEL_NAME': '13',
    'T_PURCHASE_CONTRACT.ETD_DATE': '14',
    'T_PURCHASE_CONTRACT.COMMODITY': '16',
    'T_PURCHASE_CONTRACT.ORIGIN': '17',
    'T_PURCHASE_CONTRACT.HS_CODE': '18',
    'T_PURCHASE_CONTRACT.SHIPMENT_TERM': '19',
    'T_PURCHASE_CONTRACT.UNIT_PRICE': '20',
    'T_PURCHASE_CONTRACT.NET_WEIGHT': '21',
    'T_PURCHASE_CONTRACT.GROSS_WEIGHT': '22',
    'T_PURCHASE_CONTRACT.NUMBER_OF_CONTAINERS': '23',
    'T_PURCHASE_CONTRACT.LC_NO': '24',
    'T_PURCHASE_CONTRACT.LC_DATE': '25',
    'T_PURCHASE_CONTRACT_WEIGHT_TICKET_DETAIL.NET_WEIGHT': '21',
    'T_PURCHASE_CONTRACT_WEIGHT_TICKET_DETAIL.GROSS_WEIGHT': '22',
    'T_PURCHASE_CONTRACT_WEIGHT_TICKET_DETAIL.CONTAINER_NUMBER': '30',
    'T_PURCHASE_CONTRACT_SHIPPING_SCHEDULE.SHIP_NAME': '13',
    'T_PURCHASE_CONTRACT_SHIPPING_SCHEDULE.ETD_DATE': '14',
    'T_PURCHASE_CONTRACT_SHIPPING_SCHEDULE.EXPORT_PORT': '11',
    'T_PURCHASE_CONTRACT_SHIPPING_SCHEDULE.IMPORT_PORT': '12',
    'T_PURCHASE_CONTRACT_SHIPPING_SCHEDULE.CONTAINER_QUANTITY': '23',
    'T_PURCHASE_CONTRACT_SHIPPING_SCHEDULE.BOOKING_NUMBER': '28',
    'T_PURCHASE_CONTRACT_SHIPPING_SCHEDULE.ETA_DATE': '29',
    'T_PURCHASE_CONTRACT_GOOD.GOOD_TYPE': '16',
    'T_PURCHASE_CONTRACT_GOOD.QUANTITY': '21',
    'T_PURCHASE_CONTRACT_GOOD.UNIT': '27',
    'T_PURCHASE_CONTRACT_GOOD.HS_CODE': '18',
    'T_PURCHASE_CONTRACT.CODE': '2',
    'T_PURCHASE_CONTRACT.SHIPMENT_TERM': '10',
    'T_PURCHASE_CONTRACT.LC_NO': '9',
}

def process_replacements(data: dict) -> dict:
    flat_replacements = {}
    if "replacements" in data and isinstance(data["replacements"], dict):
        flat_replacements = {k: str(v or "") for k, v in data["replacements"].items()}
    else:
        flat_dict = flatten(data, reducer='dot')
        logger.debug(f"Flattened input: {flat_dict}")

        seller_id = flat_dict.get('T_PURCHASE_CONTRACT.SELLER_ID')
        if seller_id in SELLER_NAME_MAP:
            flat_replacements['1'] = SELLER_NAME_MAP[seller_id]

        buyer_id = flat_dict.get('T_PURCHASE_CONTRACT.BUYER_ID')
        if buyer_id in BUYER_NAME_MAP:
            flat_replacements['4'] = BUYER_NAME_MAP[buyer_id]

        for flat_key, flat_value in flat_dict.items():
            if flat_key in PLACEHOLDER_MAP:
                placeholder = PLACEHOLDER_MAP[flat_key]
                flat_replacements[placeholder] = str(flat_value or "")

        flat_replacements.update({
            '5': '',
            '6': '',
            '7': '',
            '15': ''
        })

    if '21' in flat_replacements and '20' in flat_replacements:
        try:
            quantity = float(flat_replacements.get('21', 0))
            unit_price = float(flat_replacements.get('20', 0))
            grand_total = quantity * unit_price
            flat_replacements['26'] = f"USD {grand_total:,.2f}"
            logger.debug(f"Calculated GRAND TOTAL (26): {flat_replacements['26']}")
        except ValueError:
            raise ValueError("Invalid number for quantity or unit price")

    return flat_replacements