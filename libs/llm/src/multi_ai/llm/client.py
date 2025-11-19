import logging
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from multi_ai.core.settings import settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.llm.base_url,
            api_key=settings.llm.api_key,
        )
        # DÜZELTME: settings.llm.model_name kullanıyoruz
        self.model = settings.llm.model_name

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(self, prompt: str, system_prompt: str = 'You are a helpful AI assistant.') -> str:
        logger.info(f'🧠 LLM Request ({self.model}): {prompt[:50]}...')
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt},
                ],
                temperature=settings.llm.temperature,
            )
            
            content = response.choices[0].message.content
            logger.info('✅ LLM Response Received')
            return content
            
        except Exception as e:
            logger.error(f'🔥 LLM Error: {e}')
            raise e

llm_client = LLMClient()
