output "instance_ip" {
  description = "The public ip for ssh access"
  value       = aws_eip.eip.public_ip
}
