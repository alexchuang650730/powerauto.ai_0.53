# PowerAutomation Terraform输出值

# VPC输出
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "VPC CIDR块"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnet_ids" {
  description = "公有子网ID列表"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "私有子网ID列表"
  value       = module.vpc.private_subnet_ids
}

output "database_subnet_ids" {
  description = "数据库子网ID列表"
  value       = module.vpc.database_subnet_ids
}

# RDS输出
output "rds_endpoint" {
  description = "RDS数据库端点"
  value       = module.rds.database_endpoint
  sensitive   = true
}

output "rds_port" {
  description = "RDS数据库端口"
  value       = module.rds.database_port
}

output "rds_instance_id" {
  description = "RDS实例ID"
  value       = module.rds.instance_id
}

# ElastiCache输出
output "redis_endpoint" {
  description = "Redis集群端点"
  value       = module.elasticache.redis_endpoint
  sensitive   = true
}

output "redis_port" {
  description = "Redis端口"
  value       = module.elasticache.redis_port
}

# ECS输出
output "ecs_cluster_name" {
  description = "ECS集群名称"
  value       = module.ecs.cluster_name
}

output "ecs_cluster_arn" {
  description = "ECS集群ARN"
  value       = module.ecs.cluster_arn
}

output "ecs_service_names" {
  description = "ECS服务名称列表"
  value       = module.ecs.service_names
}

# ALB输出
output "alb_dns_name" {
  description = "ALB DNS名称"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "ALB托管区域ID"
  value       = module.alb.alb_zone_id
}

output "alb_arn" {
  description = "ALB ARN"
  value       = module.alb.alb_arn
}

# S3输出
output "static_assets_bucket" {
  description = "静态资源S3存储桶名称"
  value       = module.s3.static_assets_bucket_name
}

output "recording_data_bucket" {
  description = "录制数据S3存储桶名称"
  value       = module.s3.recording_data_bucket_name
}

output "backup_bucket" {
  description = "备份S3存储桶名称"
  value       = module.s3.backup_bucket_name
}

output "logs_bucket" {
  description = "日志S3存储桶名称"
  value       = module.s3.logs_bucket_name
}

# CloudFront输出
output "cloudfront_distribution_id" {
  description = "CloudFront分发ID"
  value       = module.cloudfront.distribution_id
}

output "cloudfront_domain_name" {
  description = "CloudFront域名"
  value       = module.cloudfront.distribution_domain_name
}

# Lambda输出
output "lambda_function_names" {
  description = "Lambda函数名称列表"
  value       = module.lambda.function_names
}

output "lambda_function_arns" {
  description = "Lambda函数ARN列表"
  value       = module.lambda.function_arns
  sensitive   = true
}

# API Gateway输出
output "api_gateway_url" {
  description = "API Gateway URL"
  value       = module.api_gateway.api_url
}

output "api_gateway_id" {
  description = "API Gateway ID"
  value       = module.api_gateway.api_id
}

# Route 53输出
output "domain_name" {
  description = "主域名"
  value       = var.domain_name
}

output "hosted_zone_id" {
  description = "Route 53托管区域ID"
  value       = module.route53.hosted_zone_id
}

# IAM输出
output "ecs_task_role_arn" {
  description = "ECS任务角色ARN"
  value       = module.iam.ecs_task_role_arn
}

output "lambda_execution_role_arn" {
  description = "Lambda执行角色ARN"
  value       = module.iam.lambda_execution_role_arn
}

# 监控输出
output "cloudwatch_log_groups" {
  description = "CloudWatch日志组列表"
  value       = module.monitoring.log_group_names
}

output "sns_topic_arn" {
  description = "SNS通知主题ARN"
  value       = module.monitoring.sns_topic_arn
}

# 安全组输出
output "alb_security_group_id" {
  description = "ALB安全组ID"
  value       = module.security_groups.alb_security_group_id
}

output "ecs_security_group_id" {
  description = "ECS安全组ID"
  value       = module.security_groups.ecs_security_group_id
}

output "rds_security_group_id" {
  description = "RDS安全组ID"
  value       = module.security_groups.rds_security_group_id
}

output "elasticache_security_group_id" {
  description = "ElastiCache安全组ID"
  value       = module.security_groups.elasticache_security_group_id
}

# 部署信息
output "deployment_info" {
  description = "部署信息摘要"
  value = {
    environment     = var.environment
    region         = var.aws_region
    vpc_id         = module.vpc.vpc_id
    cluster_name   = module.ecs.cluster_name
    database_endpoint = module.rds.database_endpoint
    redis_endpoint = module.elasticache.redis_endpoint
    alb_dns        = module.alb.alb_dns_name
    cloudfront_domain = module.cloudfront.distribution_domain_name
    api_gateway_url = module.api_gateway.api_url
  }
  sensitive = true
}

