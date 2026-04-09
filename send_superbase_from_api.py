import json
from supabase import create_client

# Данные из настроек Supabase
url = "url"
key = "key"
supabase = create_client(url, key)

# Открываем файл
with open('mock_orders.json', 'r', encoding='utf-8') as f:
    orders_data = json.load(f)

for order in orders_data:
    # Считаем общую сумму заказа из списка товаров
    total_sum = sum(item['initialPrice'] * item['quantity'] for item in order['items'])

    # Готовим данные для вставки
    data = {
        "first_name": order['firstName'],
        "last_name": order['lastName'],
        "total_sum": total_sum,
        "city": order['delivery']['address']['city'],
        "status": order['status'],
        "external_id": order.get('phone')  # Используем телефон как временный ID
    }

    # Отправляем в базу
    response = supabase.table("orders").insert(data).execute()
    print(f"Заказ для {order['firstName']} загружен")
