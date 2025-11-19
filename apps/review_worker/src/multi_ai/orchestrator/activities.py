from temporalio import activity
from dataclasses import dataclass

@dataclass
class AgentInput:
    task_id: str
    instruction: str
    context: dict

@dataclass
class AgentOutput:
    task_id: str
    result: str
    status: str = "success"

class AgentActivities:
    @activity.defn
    async def architect_design(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f"🏗️ Architect is designing: {input.instruction}")
        # İleride buraya LLM çağrısı gelecek
        return AgentOutput(
            task_id=input.task_id,
            result="Architecture Design: [1. API, 2. DB, 3. Worker]",
        )

    @activity.defn
    async def coder_implement(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f"💻 Coder is coding based on: {input.instruction}")
        return AgentOutput(
            task_id=input.task_id,
            result="def main(): print('Hello Enterprise AI')",
        )