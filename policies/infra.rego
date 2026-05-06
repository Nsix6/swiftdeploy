package swiftdeploy.infra

default allow := true

deny_reason contains msg if {
input.disk_free_gb < 10
msg := "Disk free is below 10GB"
}

deny_reason contains msg if {
input.cpu_load > 2.0
msg := "CPU load is above 2.0"
}

allow := false if {
count(deny_reason) > 0
}

reason := concat("; ", deny_reason)
