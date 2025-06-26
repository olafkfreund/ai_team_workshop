using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AdvancedCopilotSample
{
    public class DataProcessor
    {
        public async Task<List<int>> ProcessAsync(List<int> data)
        {
            var tasks = data.Select(async x => await SquareAsync(x));
            return (await Task.WhenAll(tasks)).ToList();
        }

        private async Task<int> SquareAsync(int x)
        {
            await Task.Delay(100);
            return x * x;
        }
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            var processor = new DataProcessor();
            var results = await processor.ProcessAsync(new List<int> { 1, 2, 3, 4, 5 });
            Console.WriteLine($"Squared results: {string.Join(", ", results)}");
        }
    }
}
