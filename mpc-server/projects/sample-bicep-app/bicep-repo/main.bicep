// Advanced Bicep sample for Copilot testing
param numbers array = [1, 2, 3, 4, 5]
var squared = [for n in numbers: n * n]
output squaredResults array = squared
