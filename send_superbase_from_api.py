import json
import requests

# 1. ТВОИ ДАННЫЕ
CRM_URL = "CRM_URL"  # Твой URL
API_KEY = "api_key"  # Твой ключ

# Путь к API методу для создания заказов
endpoint = f"{CRM_URL}/api/v5/orders/create"

# 2. ЧИТАЕМ ФАЙЛ
with open('mock_orders.json', 'r', encoding='utf-8') as f:
    orders_data = json.load(f)

print(f"Начинаю загрузку {len(orders_data)} заказов в RetailCRM...")

for i, order in enumerate(orders_data):
    # Преобразуем формат JSON под требования RetailCRM API
    payload = {
        "site": "hipiqmpz",  # Укажи символьный код твоего магазина из настроек CRM
        "order": json.dumps({
            "firstName": order['firstName'],
            "lastName": order['lastName'],
            "phone": order['phone'],
            "email": order['email'],
            "orderMethod": "shopping-cart",
            "items": [
                {
                    "initialPrice": item['initialPrice'],
                    "productName": item['productName'],
                    "quantity": item['quantity']
                } for item in order['items']
            ],
            "delivery": {
                "address": {
                    "city": order['delivery']['address']['city'],
                    "text": order['delivery']['address']['text']
                }
            }
        })
    }

    # Отправляем запрос
    response = requests.post(endpoint, data=payload, params={"apiKey": API_KEY})
    print(f"Отправка запроса на: {endpoint}")

    if response.status_code == 201:
        print(f"[{i + 1}/50] Заказ для {order['firstName']} успешно создан!")
    else:
        print(f"Ошибка при загрузке заказа {i + 1}: {response.text}")

print("Готово!")
