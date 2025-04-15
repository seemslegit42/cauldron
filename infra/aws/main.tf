# Cauldron Infrastructure - Main Terraform Configuration

# Terraform configuration
terraform {
  required_version = ">= 1.0.0"
  
  # Backend configuration for state storage
  # Uncomment and configure when ready to use remote state
  # backend "s3" {
  #   bucket         = "cauldron-terraform-state"
  #   key            = "terraform.tfstate"
  #   region         = "us-west-2"
  #   dynamodb_table = "cauldron-terraform-locks"
  #   encrypt        = true
  # }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Local variables
locals {
  project     = "cauldron"
  environment = var.environment
  tags = {
    Project     = local.project
    Environment = local.environment
    ManagedBy   = "Terraform"
  }
}

# Create a VPC for the Cauldron infrastructure
module "vpc" {
  source = "../modules/vpc"
  
  project     = local.project
  environment = local.environment
  cidr_block  = var.vpc_cidr
  tags        = local.tags
}

# Create an ECS cluster for container orchestration
module "ecs" {
  source = "../modules/ecs"
  
  project     = local.project
  environment = local.environment
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
  tags        = local.tags
}

# Create an RDS instance for PostgreSQL
module "rds" {
  source = "../modules/rds"
  
  project     = local.project
  environment = local.environment
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.database_subnet_ids
  tags        = local.tags
  
  db_name     = var.db_name
  db_username = var.db_username
  db_password = var.db_password
}

# Create an ElastiCache cluster for Redis
module "elasticache" {
  source = "../modules/elasticache"
  
  project     = local.project
  environment = local.environment
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.database_subnet_ids
  tags        = local.tags
}

# Create S3 buckets for storage
module "s3" {
  source = "../modules/s3"
  
  project     = local.project
  environment = local.environment
  tags        = local.tags
}

# Create security groups and IAM roles
module "security" {
  source = "../modules/security"
  
  project     = local.project
  environment = local.environment
  vpc_id      = module.vpc.vpc_id
  tags        = local.tags
}

# Create load balancers for the services
module "load_balancer" {
  source = "../modules/load_balancer"
  
  project     = local.project
  environment = local.environment
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.public_subnet_ids
  tags        = local.tags
}
