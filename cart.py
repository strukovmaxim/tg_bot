from data import carts, id_to_item

def get_cart_text(user_id: int, items: dict[int, int] | None = None) -> str:
    """Формирует список товаров корзины (или переданных items для истории)"""
    items = items if items is not None else carts.get(user_id, {})
    if not items:
        return "Корзина пуста."
    lines = []
    for item_id, qty in items.items():
        item = id_to_item[item_id]
        lines.append(f"{item['name']} — {qty} шт. × {item['price']}₽ = {qty * item['price']}₽")
    return "\n".join(lines)

def cart_totals(items: dict[int, int]) -> tuple[int, int]:
    """Возвращает (наличные, безнал +9%)"""
    total = sum(id_to_item[i]["price"] * q for i, q in items.items())
    return total, int(total * 1.09)
