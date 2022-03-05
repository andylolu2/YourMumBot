output "instance_ip" {
  description = "The public ip for ssh access"
  value       = digitalocean_floating_ip.floating_ip.ip_address
}
