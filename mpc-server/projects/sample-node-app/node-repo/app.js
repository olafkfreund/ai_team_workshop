// Advanced Node.js sample for Copilot testing
const fs = require('fs').promises;

class DataProcessor {
  constructor(data) {
    this.data = data;
  }

  async process() {
    const results = await Promise.all(this.data.map(x => this._square(x)));
    return results;
  }

  async _square(x) {
    await new Promise(res => setTimeout(res, 100));
    return x * x;
  }
}

(async () => {
  const processor = new DataProcessor([1, 2, 3, 4, 5]);
  const results = await processor.process();
  console.log(`Squared results: ${results}`);
})();
