terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.47"
    }
  }
  required_version = ">= 1.0.1"
}

provider "aws" {
  profile = "default"
  region  = var.aws_region
}

data "aws_ami" "aws_linux_2" {
  most_recent = true

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-2.0.????????.?-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["amazon"]
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "aws_ec2"
  public_key = file("~/.ssh/aws-ec2.pub")
}

resource "aws_vpc" "vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    "Name" = "${var.tag}VPC"
  }
}

resource "aws_eip" "eip" {
  instance = aws_instance.app_server.id
  vpc      = true
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    "Name" = "${var.tag}GateWay"
  }
}

resource "aws_subnet" "subnet" {
  cidr_block        = cidrsubnet(aws_vpc.vpc.cidr_block, 3, 1)
  vpc_id            = aws_vpc.vpc.id
  availability_zone = var.aws_local_zone
  tags = {
    "Name" = "${var.tag}Subnet"
  }
}

resource "aws_route_table" "route_table" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  tags = {
    "Name" = "${var.tag}RouteTable"
  }
}
resource "aws_route_table_association" "route_table_association" {
  subnet_id      = aws_subnet.subnet.id
  route_table_id = aws_route_table.route_table.id
}

resource "aws_security_group" "sg_ssh" {
  name   = "sg_allow_ssh"
  vpc_id = aws_vpc.vpc.id
  ingress {
    // For SSH into EC2 instance
    protocol    = "tcp"
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
  }
  // Terraform removes the default rule
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    "Name" = "${var.tag}SecurityGroup"
  }
}

resource "aws_instance" "app_server" {
  ami                         = data.aws_ami.aws_linux_2.id
  instance_type               = var.ec2_instance_type
  vpc_security_group_ids      = ["${aws_security_group.sg_ssh.id}"]
  key_name                    = aws_key_pair.ssh_key.key_name
  associate_public_ip_address = true
  subnet_id                   = aws_subnet.subnet.id
  tags = {
    "Name" = "${var.tag}Server"
  }
}
