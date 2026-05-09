from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import AgentState

class Judgement(BaseModel):
    is_pass: bool = Field(description="回答是否正確且完整")
    reason: str = Field(description="失敗原因說明")

critic_llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0).with_structured_output(Judgement)

def critic_node(state: AgentState):
    messages = state["messages"]
    
    # 提取最後一次工具結果、AI回答、用戶需求 (邏輯同你原本的代碼)
    latest_tool_results = [m.content for m in reversed(messages) if isinstance(m, ToolMessage)]
    facts_context = "\n".join(latest_tool_results) if latest_tool_results else "本次操作未調用工具。"
    ai_final_response = messages[-1].content
    user_query = [m.content for m in messages if isinstance(m, HumanMessage)][-1]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位精準的對話稽核員..."), # 這裡放入你原本的 system prompt
        ("human", "本次工具結果：\n{facts}\n\n使用者需求：{query}\n\nAI回答：{response}")
    ])

    chain = prompt | critic_llm 
    judgement = chain.invoke({"facts": facts_context, "query": user_query, "response": ai_final_response})

    if not judgement.is_pass:
        return {
            "messages": [HumanMessage(content=f"【系統糾錯系統】：{judgement.reason}")],
            "retry_count": state.get("retry_count", 0) + 1
        }
    return {"retry_count": 0}