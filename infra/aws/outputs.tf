# Cauldron Infrastructure - Outputs

# VPC Outputs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "The IDs of the public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "The IDs of the private subnets"
  value       = module.vpc.private_subnet_ids
}

output "database_subnet_ids" {
  description = "The IDs of the database subnets"
  value       = module.vpc.database_subnet_ids
}

# RDS Outputs
output "rds_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = module.rds.endpoint
}

output "rds_port" {
  description = "The port of the RDS instance"
  value       = module.rds.port
}

# ElastiCache Outputs
output "elasticache_endpoint" {
  description = "The endpoint of the ElastiCache cluster"
  value       = module.elasticache.endpoint
}

output "elasticache_port" {
  description = "The port of the ElastiCache cluster"
  value       = module.elasticache.port
}

# ECS Outputs
output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "ecs_cluster_arn" {
  description = "The ARN of the ECS cluster"
  value       = module.ecs.cluster_arn
}

# Load Balancer Outputs
output "load_balancer_dns_name" {
  description = "The DNS name of the load balancer"
  value       = module.load_balancer.dns_name
}

output "load_balancer_zone_id" {
  description = "The zone ID of the load balancer"
  value       = module.load_balancer.zone_id
}

# S3 Outputs
output "s3_bucket_names" {
  description = "The names of the S3 buckets"
  value       = module.s3.bucket_names
}

# Security Outputs
output "security_group_ids" {
  description = "The IDs of the security groups"
  value       = module.security.security_group_ids
}
