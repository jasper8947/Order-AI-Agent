from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from graph.state import AgentState
from graph.nodes import call_model, block_action_node
from agents.critic import critic_node
from tools.order_tools import order_tools
from data.order_db import order_db
from langchain_core.messages import AIMessage, HumanMessage

# 條件路由邏輯
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        for tc in last_message.tool_calls:
            if tc["name"] in ["update_order_details", "cancel_order"]:
                order = order_db.get(tc["args"].get("order_id"))
                if order and order["status"] in ["已出貨", "已取消"]:
                    return "block_action"
        return "action"
    if isinstance(last_message, AIMessage):
        return "critic"
    return END

def router_after_critic(state: AgentState):
    last_msg = state["messages"][-1]
    if isinstance(last_msg, HumanMessage) and "【系統糾錯系統】" in last_msg.content:
        if state.get("retry_count", 0) <= 2:
            return "retry"
    return END

# 構建圖
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", ToolNode(order_tools))
workflow.add_node("block_action", block_action_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"action": "action", "block_action": "block_action", "critic": "critic", END: END})
workflow.add_conditional_edges("critic", router_after_critic, {"retry": "agent", END: END})
workflow.add_edge("action", "agent")
workflow.add_edge("block_action", "agent")

app = workflow.compile(checkpointer=MemorySaver())
# 執行一次即可生成
# app.get_graph().draw_mermaid_png(output_file_path="graph_structure.png")

async def run_agent_chat(user_input: str, session_id: str)-> str:
    config = {"configurable": {"thread_id": session_id}}

    result = await app.ainvoke(
        {"messages": [HumanMessage(content=user_input)], "retry_count": 0}, 
        config=config
    )
    
    return result["messages"][-1].content