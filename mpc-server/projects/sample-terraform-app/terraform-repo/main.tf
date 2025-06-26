# Advanced Terraform sample for Copilot testing
variable "numbers" {
  type    = list(number)
  default = [1, 2, 3, 4, 5]
}

resource "null_resource" "squared" {
  count = length(var.numbers)
  provisioner "local-exec" {
    command = "echo $(( ${var.numbers[count.index]} * ${var.numbers[count.index]} ))"
  }
}

output "squared_results" {
  value = [for n in var.numbers : n * n]
}
