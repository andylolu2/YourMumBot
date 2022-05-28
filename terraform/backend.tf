terraform {
  cloud {
    organization = "andylolu2"

    workspaces {
      name = "yourmumbot"
    }
  }
  required_version = ">= 1.1.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

data "digitalocean_ssh_key" "ssh_key" {
  name = "fedora_g14"
}
