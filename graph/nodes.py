from langchain_core.messages import SystemMessage, ToolMessage
from agents.models import model_with_tools
from data.order_db import order_db
from graph.state import AgentState

def call_model(state: AgentState):
    sys_msg = SystemMessage(content="你是一個訂單管理助手...")
    messages = [sys_msg] + list(state["messages"])
    return {"messages": [model_with_tools.invoke(messages)]}

def block_action_node(state: AgentState):
    last_message = state["messages"][-1]
    results = []
    for tool_call in last_message.tool_calls:
        order_id = tool_call["args"].get("order_id")
        status = order_db.get(order_id, {}).get("status", "未知")
        results.append(ToolMessage(
            tool_call_id=tool_call["id"],
            content=f"攔截操作：訂單 {order_id} 狀態為「{status}」，不允許修改。"
        ))
    return {"messages": results}