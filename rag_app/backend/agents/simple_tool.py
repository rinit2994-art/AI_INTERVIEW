from google.adk.tools.base_tool import BaseTool
from typing import Callable, Any, Dict

class SimpleTool(BaseTool):
    def __init__(self, name: str, description: str, func: Callable):
        super().__init__(name=name, description=description)
        self.func = func

    async def run_async(self, *, args: Dict[str, Any], tool_context: Any) -> Any:
        return self.func(**args)
