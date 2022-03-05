resource "digitalocean_droplet" "server" {
  image  = "docker-20-04"
  name   = "server"
  region = var.region
  size   = var.app_size
  ssh_keys = [
    data.digitalocean_ssh_key.do_rsa.id
  ]
  tags       = [var.tag]
  user_data  = file("cloud_init.yaml")
  monitoring = true
  ipv6       = true
}

resource "digitalocean_floating_ip" "floating_ip" {
  droplet_id = digitalocean_droplet.server.id
  region     = digitalocean_droplet.server.region
}

resource "digitalocean_firewall" "web" {
  name = "in-22-80-433-out-all"

  droplet_ids = [digitalocean_droplet.server.id]
  tags        = [var.tag]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
