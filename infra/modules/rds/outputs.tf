# RDS Module - Outputs

output "endpoint" {
  description = "The endpoint of the RDS instance"
  value       = aws_db_instance.main.endpoint
}

output "address" {
  description = "The address of the RDS instance"
  value       = aws_db_instance.main.address
}

output "port" {
  description = "The port of the RDS instance"
  value       = aws_db_instance.main.port
}

output "name" {
  description = "The name of the database"
  value       = aws_db_instance.main.db_name
}

output "username" {
  description = "The username for the database"
  value       = aws_db_instance.main.username
}

output "password" {
  description = "The password for the database"
  value       = var.db_password != "" ? var.db_password : random_password.db_password[0].result
  sensitive   = true
}

output "security_group_id" {
  description = "The ID of the security group for the RDS instance"
  value       = aws_security_group.rds.id
}

output "db_instance_id" {
  description = "The ID of the RDS instance"
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "The ARN of the RDS instance"
  value       = aws_db_instance.main.arn
}
