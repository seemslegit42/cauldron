# RDS Module - Main

# Create a DB subnet group
resource "aws_db_subnet_group" "main" {
  name        = "${var.project}-${var.environment}-db-subnet-group"
  description = "DB subnet group for ${var.project} ${var.environment}"
  subnet_ids  = var.subnet_ids
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project}-${var.environment}-db-subnet-group"
    }
  )
}

# Create a security group for the RDS instance
resource "aws_security_group" "rds" {
  name        = "${var.project}-${var.environment}-rds-sg"
  description = "Security group for RDS instance"
  vpc_id      = var.vpc_id
  
  # Allow PostgreSQL traffic from the VPC
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.selected.cidr_block]
  }
  
  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project}-${var.environment}-rds-sg"
    }
  )
}

# Get the VPC details
data "aws_vpc" "selected" {
  id = var.vpc_id
}

# Create a random password for the RDS instance if not provided
resource "random_password" "db_password" {
  count = var.db_password == "" ? 1 : 0
  
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

locals {
  db_password = var.db_password != "" ? var.db_password : random_password.db_password[0].result
}

# Create an RDS instance
resource "aws_db_instance" "main" {
  identifier              = "${var.project}-${var.environment}-db"
  engine                  = "postgres"
  engine_version          = var.db_engine_version
  instance_class          = var.db_instance_class
  allocated_storage       = var.db_allocated_storage
  max_allocated_storage   = var.db_max_allocated_storage
  storage_type            = "gp3"
  storage_encrypted       = true
  
  db_name                 = var.db_name
  username                = var.db_username
  password                = local.db_password
  port                    = 5432
  
  vpc_security_group_ids  = [aws_security_group.rds.id]
  db_subnet_group_name    = aws_db_subnet_group.main.name
  parameter_group_name    = aws_db_parameter_group.main.name
  
  backup_retention_period = var.db_backup_retention_period
  backup_window           = var.db_backup_window
  maintenance_window      = var.db_maintenance_window
  
  skip_final_snapshot     = var.db_skip_final_snapshot
  final_snapshot_identifier = var.db_skip_final_snapshot ? null : "${var.project}-${var.environment}-db-final-snapshot"
  
  deletion_protection     = var.db_deletion_protection
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project}-${var.environment}-db"
    }
  )
}

# Create a parameter group for the RDS instance
resource "aws_db_parameter_group" "main" {
  name        = "${var.project}-${var.environment}-db-pg"
  family      = "postgres15"
  description = "Parameter group for ${var.project} ${var.environment} PostgreSQL database"
  
  # Enable logical replication
  parameter {
    name  = "rds.logical_replication"
    value = "1"
    apply_method = "pending-reboot"
  }
  
  # Set timezone to UTC
  parameter {
    name  = "timezone"
    value = "UTC"
    apply_method = "pending-reboot"
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project}-${var.environment}-db-pg"
    }
  )
}
