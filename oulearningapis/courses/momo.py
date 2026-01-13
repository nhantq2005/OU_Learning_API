import json, hmac, hashlib, requests, uuid

# CẤU HÌNH MOMO (TÀI KHOẢN TEST - KHÔNG DÙNG CHO PRODUCTION)
MOMO_CONFIG = {
    'partnerCode': 'MOMO',
    'accessKey': 'F8BBA842ECF85',
    'secretKey': 'K951B6PE1waDMi640xX08PD3vg6EkVlz',
    'endpoint': 'https://test-payment.momo.vn/v2/gateway/api/create',
    # QUAN TRỌNG: Đây phải là đường dẫn public (dùng Ngrok nếu chạy localhost)
    'ipnUrl': 'https://your-ngrok-domain.ngrok-free.app/api/payment/momo-ipn/',
    'redirectUrl': 'momo://app',  # Chuyển hướng về lại App sau khi thanh toán
}


def create_payment(order_id, amount, order_info):
    partnerCode = MOMO_CONFIG['partnerCode']
    accessKey = MOMO_CONFIG['accessKey']
    secretKey = MOMO_CONFIG['secretKey']
    requestId = str(uuid.uuid4())

    # Tạo chuỗi chữ ký (Signature) theo chuẩn MoMo
    raw_signature = f"accessKey={accessKey}&amount={amount}&extraData=&ipnUrl={MOMO_CONFIG['ipnUrl']}&orderId={order_id}&orderInfo={order_info}&partnerCode={partnerCode}&redirectUrl={MOMO_CONFIG['redirectUrl']}&requestId={requestId}&requestType=captureWallet"

    # Mã hóa HMAC SHA256
    h = hmac.new(bytes(secretKey, 'ascii'), bytes(raw_signature, 'utf-8'), hashlib.sha256)
    signature = h.hexdigest()

    # Dữ liệu gửi sang MoMo
    data = {
        'partnerCode': partnerCode,
        'partnerName': "OU Learning",
        'storeId': "MomoTestStore",
        'requestId': requestId,
        'amount': amount,
        'orderId': order_id,
        'orderInfo': order_info,
        'redirectUrl': MOMO_CONFIG['redirectUrl'],
        'ipnUrl': MOMO_CONFIG['ipnUrl'],
        'lang': 'vi',
        'extraData': "",
        'requestType': 'captureWallet',
        'signature': signature
    }

    try:
        response = requests.post(MOMO_CONFIG['endpoint'], json=data)
        return response.json()
    except Exception as e:
        print(f"Lỗi kết nối MoMo: {e}")
        return None