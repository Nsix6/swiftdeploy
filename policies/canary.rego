package swiftdeploy.canary

default allow := true

deny_reason contains msg if {
input.error_rate > 0.01
msg := "Error rate exceeded 1%"
}

deny_reason contains msg if {
input.p99_latency_ms > 500
msg := "P99 latency exceeded 500ms"
}

allow := false if {
count(deny_reason) > 0
}

reason := concat("; ", deny_reason)
