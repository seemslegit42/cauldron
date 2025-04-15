# Cauldron Infrastructure - Provider Configuration

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  
  # Default tags applied to all resources
  default_tags {
    tags = {
      Project     = "cauldron"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
