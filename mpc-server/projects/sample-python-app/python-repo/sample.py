"""
Sample Python code for advanced Copilot testing
"""
import asyncio
from typing import List

class DataProcessor:
    """Processes data asynchronously."""
    def __init__(self, data: List[int]):
        self.data = data

    async def process(self):
        results = await asyncio.gather(*(self._square(x) for x in self.data))
        return results

    async def _square(self, x: int) -> int:
        await asyncio.sleep(0.1)
        return x * x

async def main():
    processor = DataProcessor([1, 2, 3, 4, 5])
    results = await processor.process()
    print(f"Squared results: {results}")

if __name__ == "__main__":
    asyncio.run(main())
