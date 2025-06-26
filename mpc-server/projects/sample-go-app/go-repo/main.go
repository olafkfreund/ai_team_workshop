// Advanced Go sample for Copilot testing
package main

import (
	"fmt"
	"sync"
	"time"
)

type DataProcessor struct {
	data []int
}

func (p *DataProcessor) Process() []int {
	var wg sync.WaitGroup
	results := make([]int, len(p.data))
	for i, x := range p.data {
		wg.Add(1)
		go func(i, x int) {
			defer wg.Done()
			time.Sleep(100 * time.Millisecond)
			results[i] = x * x
		}(i, x)
	}
	wg.Wait()
	return results
}

func main() {
	processor := DataProcessor{data: []int{1, 2, 3, 4, 5}}
	results := processor.Process()
	fmt.Printf("Squared results: %v\n", results)
}
