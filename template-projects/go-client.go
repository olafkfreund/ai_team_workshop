package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

func main() {
	agent := "azureVmMetricsAgent"
	mpcServer := "http://localhost:8080"
	prompt := "Check the CPU and network metrics for VM 'webserver01' in resource group 'prod-rg'."

	body, _ := json.Marshal(map[string]string{"prompt": prompt})
	resp, err := http.Post(fmt.Sprintf("%s/agent/%s", mpcServer, agent), "application/json", bytes.NewBuffer(body))
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	fmt.Println(result)
}
