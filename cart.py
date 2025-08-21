from data import carts, id_to_item

def cart_totals(cart: dict[int, int]) -> tuple[int, int]:
    total = sum(id_to_item[iid]["price"] * qty for iid, qty in cart.items())
    return total, int(total * 1.09)

def get_cart_text(user_id: int) -> str:
    cart = carts.get(user_id, {})
    if not cart:
        return "🛒 Корзина пуста."
    lines = ["🛒 Ваша корзина:\n"]
    for iid, qty in cart.items():
        item = id_to_item[iid]
        lines.append(f"- {item['name']} × {qty} — {item['price']*qty}₽")
    nal, beznal = cart_totals(cart)
    lines.append(f"\n💰 Наличные: {nal}₽")
    lines.append(f"💳 Безнал (+9%): {beznal}₽")
    return "\n".join(lines)
