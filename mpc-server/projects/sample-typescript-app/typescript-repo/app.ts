// Advanced TypeScript sample for Copilot testing
class DataProcessor {
  data: number[];
  constructor(data: number[]) {
    this.data = data;
  }
  async process(): Promise<number[]> {
    const results = await Promise.all(this.data.map(x => this._square(x)));
    return results;
  }
  private async _square(x: number): Promise<number> {
    await new Promise(res => setTimeout(res, 100));
    return x * x;
  }
}
(async () => {
  const processor = new DataProcessor([1, 2, 3, 4, 5]);
  const results = await processor.process();
  console.log(`Squared results: ${results}`);
})();
