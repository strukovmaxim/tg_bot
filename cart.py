from data import carts, id_to_item


def get_cart_text(user_id, items=None):
    """Формирует список товаров корзины или переданных items"""
    if items is None:
        items = carts.get(user_id, {})

    if not items:
        return "Корзина пуста."

    lines = []
    for item_id, qty in items.items():
        item = id_to_item[item_id]
        lines.append(f"{item['name']} — {qty} шт. × {item['price']}₽ = {qty * item['price']}₽")

    return "\n".join(lines)


def cart_totals(items):
    """Считает итоговые суммы"""
    total = sum(id_to_item[i]["price"] * q for i, q in items.items())
    nal = total
    beznal = int(total * 1.09)  # +9%
    return nal, beznal
