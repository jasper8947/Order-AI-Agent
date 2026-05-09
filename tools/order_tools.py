from langchain_core.tools import tool
from data.order_db import order_db

@tool
def get_order_details(order_id: str) -> str:
    """根據訂單編號查詢訂單詳細資訊。"""
    order = order_db.get(order_id)
    return f"訂單 {order_id} 資訊：{order}" if order else f"找不到訂單編號 {order_id}。"

@tool
def update_order_details(order_id: str, new_quantity: int = None, new_address: str = None) -> str:
    """修改指定訂單的購買數量或地址。"""
    if order_id not in order_db:
        return f"修改失敗，找不到訂單 {order_id}。"
    
    updates = []
    if new_quantity is not None:
        order_db[order_id]["quantity"] = new_quantity
        updates.append(f"數量更新為 {new_quantity}")
    if new_address is not None:
        order_db[order_id]["address"] = new_address
        updates.append(f"地址更新為 {new_address}")
    
    return f"訂單 {order_id} 已成功更新：" + "、".join(updates)

@tool
def cancel_order(order_id: str) -> str:
    """取消指定的訂單。"""
    if order_id not in order_db:
        return f"取消失敗，找不到訂單 {order_id}。"
    order_db[order_id]["status"] = "已取消"
    return f"訂單 {order_id} 已成功取消。"

order_tools = [get_order_details, update_order_details, cancel_order]