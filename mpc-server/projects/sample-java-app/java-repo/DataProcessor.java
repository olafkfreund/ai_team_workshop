// Advanced Java sample for Copilot testing
import java.util.*;
import java.util.concurrent.*;

public class DataProcessor {
    private List<Integer> data;
    public DataProcessor(List<Integer> data) {
        this.data = data;
    }
    public List<Integer> process() throws InterruptedException, ExecutionException {
        ExecutorService executor = Executors.newFixedThreadPool(data.size());
        List<Future<Integer>> futures = new ArrayList<>();
        for (int x : data) {
            futures.add(executor.submit(() -> {
                Thread.sleep(100);
                return x * x;
            }));
        }
        List<Integer> results = new ArrayList<>();
        for (Future<Integer> f : futures) {
            results.add(f.get());
        }
        executor.shutdown();
        return results;
    }
    public static void main(String[] args) throws Exception {
        DataProcessor processor = new DataProcessor(Arrays.asList(1, 2, 3, 4, 5));
        List<Integer> results = processor.process();
        System.out.println("Squared results: " + results);
    }
}
