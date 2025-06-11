# PowerAutomation AWS部署配置
# 主要配置文件，定义所有AWS资源

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "powerautomation-terraform-state"
    key            = "v0571/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "powerautomation-terraform-locks"
    encrypt        = true
  }
}

# AWS Provider配置
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "PowerAutomation"
      Version     = "v0.571"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# 数据源
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# 本地变量
locals {
  name_prefix = "powerauto-${var.environment}"
  
  common_tags = {
    Project     = "PowerAutomation"
    Version     = "v0.571"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  
  azs = slice(data.aws_availability_zones.available.names, 0, 3)
}

# VPC模块
module "vpc" {
  source = "./modules/vpc"
  
  name_prefix = local.name_prefix
  cidr_block  = var.vpc_cidr
  azs         = local.azs
  
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  database_subnet_cidrs = var.database_subnet_cidrs
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true
  
  tags = local.common_tags
}

# 安全组模块
module "security_groups" {
  source = "./modules/security"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  
  tags = local.common_tags
}

# RDS数据库模块
module "rds" {
  source = "./modules/rds"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.database_subnet_ids
  
  security_group_ids = [module.security_groups.rds_security_group_id]
  
  engine_version    = var.rds_engine_version
  instance_class    = var.rds_instance_class
  allocated_storage = var.rds_allocated_storage
  
  database_name = var.database_name
  username      = var.database_username
  password      = var.database_password
  
  backup_retention_period = var.rds_backup_retention
  backup_window          = var.rds_backup_window
  maintenance_window     = var.rds_maintenance_window
  
  multi_az               = var.environment == "production"
  deletion_protection    = var.environment == "production"
  
  tags = local.common_tags
}

# ElastiCache Redis模块
module "elasticache" {
  source = "./modules/elasticache"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
  
  security_group_ids = [module.security_groups.elasticache_security_group_id]
  
  node_type          = var.elasticache_node_type
  num_cache_nodes    = var.elasticache_num_nodes
  parameter_group    = var.elasticache_parameter_group
  engine_version     = var.elasticache_engine_version
  
  tags = local.common_tags
}

# ECS集群模块
module "ecs" {
  source = "./modules/ecs"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
  
  security_group_ids = [module.security_groups.ecs_security_group_id]
  
  cluster_name = "${local.name_prefix}-cluster"
  
  # 企业版服务配置
  enterprise_service_config = {
    cpu    = var.enterprise_cpu
    memory = var.enterprise_memory
    count  = var.enterprise_desired_count
  }
  
  # 个人专业版服务配置
  personal_service_config = {
    cpu    = var.personal_cpu
    memory = var.personal_memory
    count  = var.personal_desired_count
  }
  
  # Kilo Code引擎配置
  kilo_code_service_config = {
    cpu    = var.kilo_code_cpu
    memory = var.kilo_code_memory
    count  = var.kilo_code_desired_count
  }
  
  tags = local.common_tags
}

# Application Load Balancer模块
module "alb" {
  source = "./modules/alb"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.public_subnet_ids
  
  security_group_ids = [module.security_groups.alb_security_group_id]
  
  certificate_arn = var.ssl_certificate_arn
  
  tags = local.common_tags
}

# S3存储模块
module "s3" {
  source = "./modules/s3"
  
  name_prefix = local.name_prefix
  
  # 静态资源存储桶
  static_assets_bucket = "${local.name_prefix}-static-assets"
  
  # 录制数据存储桶
  recording_data_bucket = "${local.name_prefix}-recording-data"
  
  # 备份存储桶
  backup_bucket = "${local.name_prefix}-backups"
  
  # 日志存储桶
  logs_bucket = "${local.name_prefix}-logs"
  
  tags = local.common_tags
}

# CloudFront CDN模块
module "cloudfront" {
  source = "./modules/cloudfront"
  
  name_prefix = local.name_prefix
  
  # S3源站配置
  s3_bucket_domain = module.s3.static_assets_bucket_domain
  
  # ALB源站配置
  alb_domain = module.alb.alb_dns_name
  
  # SSL证书
  certificate_arn = var.cloudfront_certificate_arn
  
  tags = local.common_tags
}

# Lambda函数模块
module "lambda" {
  source = "./modules/lambda"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
  
  security_group_ids = [module.security_groups.lambda_security_group_id]
  
  # 环境变量
  environment_variables = {
    DATABASE_URL = module.rds.database_endpoint
    REDIS_URL    = module.elasticache.redis_endpoint
    S3_BUCKET    = module.s3.recording_data_bucket_name
  }
  
  tags = local.common_tags
}

# API Gateway模块
module "api_gateway" {
  source = "./modules/api_gateway"
  
  name_prefix = local.name_prefix
  
  # Lambda集成
  lambda_function_arns = module.lambda.function_arns
  
  # 认证配置
  cognito_user_pool_arn = var.cognito_user_pool_arn
  
  tags = local.common_tags
}

# CloudWatch监控模块
module "monitoring" {
  source = "./modules/monitoring"
  
  name_prefix = local.name_prefix
  
  # ECS集群监控
  ecs_cluster_name = module.ecs.cluster_name
  ecs_service_names = module.ecs.service_names
  
  # RDS监控
  rds_instance_id = module.rds.instance_id
  
  # ElastiCache监控
  elasticache_cluster_id = module.elasticache.cluster_id
  
  # ALB监控
  alb_arn_suffix = module.alb.alb_arn_suffix
  
  # SNS通知主题
  notification_email = var.notification_email
  
  tags = local.common_tags
}

# Route 53 DNS模块
module "route53" {
  source = "./modules/route53"
  
  domain_name = var.domain_name
  
  # CloudFront分发
  cloudfront_domain = module.cloudfront.distribution_domain_name
  cloudfront_zone_id = module.cloudfront.distribution_hosted_zone_id
  
  # ALB记录
  alb_domain = module.alb.alb_dns_name
  alb_zone_id = module.alb.alb_zone_id
  
  tags = local.common_tags
}

# IAM角色和策略模块
module "iam" {
  source = "./modules/iam"
  
  name_prefix = local.name_prefix
  
  # S3存储桶ARN
  s3_bucket_arns = [
    module.s3.static_assets_bucket_arn,
    module.s3.recording_data_bucket_arn,
    module.s3.backup_bucket_arn,
    module.s3.logs_bucket_arn
  ]
  
  tags = local.common_tags
}

