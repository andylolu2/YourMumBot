output "instance_ip" {
  description = "The public ip for ssh access"
  value       = digitalocean_droplet.server.ipv4_address
}
