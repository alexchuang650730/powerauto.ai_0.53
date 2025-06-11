# PowerAutomation Terraform变量定义

# 基础配置
variable "aws_region" {
  description = "AWS部署区域"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "部署环境"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "环境必须是: development, staging, production"
  }
}

variable "domain_name" {
  description = "主域名"
  type        = string
  default     = "powerautomation.ai"
}

# 网络配置
variable "vpc_cidr" {
  description = "VPC CIDR块"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "公有子网CIDR列表"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "私有子网CIDR列表"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

variable "database_subnet_cidrs" {
  description = "数据库子网CIDR列表"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
}

# RDS数据库配置
variable "rds_engine_version" {
  description = "PostgreSQL引擎版本"
  type        = string
  default     = "15.4"
}

variable "rds_instance_class" {
  description = "RDS实例类型"
  type        = string
  default     = "db.r6g.2xlarge"
}

variable "rds_allocated_storage" {
  description = "RDS存储大小(GB)"
  type        = number
  default     = 2000
}

variable "database_name" {
  description = "数据库名称"
  type        = string
  default     = "powerautomation"
}

variable "database_username" {
  description = "数据库用户名"
  type        = string
  default     = "powerauto_admin"
}

variable "database_password" {
  description = "数据库密码"
  type        = string
  sensitive   = true
}

variable "rds_backup_retention" {
  description = "RDS备份保留天数"
  type        = number
  default     = 30
}

variable "rds_backup_window" {
  description = "RDS备份时间窗口"
  type        = string
  default     = "03:00-04:00"
}

variable "rds_maintenance_window" {
  description = "RDS维护时间窗口"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

# ElastiCache配置
variable "elasticache_node_type" {
  description = "ElastiCache节点类型"
  type        = string
  default     = "cache.r6g.xlarge"
}

variable "elasticache_num_nodes" {
  description = "ElastiCache节点数量"
  type        = number
  default     = 6
}

variable "elasticache_parameter_group" {
  description = "ElastiCache参数组"
  type        = string
  default     = "default.redis7"
}

variable "elasticache_engine_version" {
  description = "Redis引擎版本"
  type        = string
  default     = "7.0"
}

# ECS服务配置
variable "enterprise_cpu" {
  description = "企业版服务CPU"
  type        = number
  default     = 8192  # 8 vCPU
}

variable "enterprise_memory" {
  description = "企业版服务内存(MB)"
  type        = number
  default     = 16384  # 16 GB
}

variable "enterprise_desired_count" {
  description = "企业版服务实例数"
  type        = number
  default     = 8
}

variable "personal_cpu" {
  description = "个人专业版服务CPU"
  type        = number
  default     = 4096  # 4 vCPU
}

variable "personal_memory" {
  description = "个人专业版服务内存(MB)"
  type        = number
  default     = 8192  # 8 GB
}

variable "personal_desired_count" {
  description = "个人专业版服务实例数"
  type        = number
  default     = 4
}

variable "kilo_code_cpu" {
  description = "Kilo Code引擎CPU"
  type        = number
  default     = 16384  # 16 vCPU
}

variable "kilo_code_memory" {
  description = "Kilo Code引擎内存(MB)"
  type        = number
  default     = 32768  # 32 GB
}

variable "kilo_code_desired_count" {
  description = "Kilo Code引擎实例数"
  type        = number
  default     = 6
}

# SSL证书配置
variable "ssl_certificate_arn" {
  description = "SSL证书ARN (ALB使用)"
  type        = string
  default     = ""
}

variable "cloudfront_certificate_arn" {
  description = "CloudFront SSL证书ARN"
  type        = string
  default     = ""
}

# Cognito配置
variable "cognito_user_pool_arn" {
  description = "Cognito用户池ARN"
  type        = string
  default     = ""
}

# 监控配置
variable "notification_email" {
  description = "告警通知邮箱"
  type        = string
  default     = "alerts@powerautomation.ai"
}

# 标签配置
variable "additional_tags" {
  description = "额外的资源标签"
  type        = map(string)
  default     = {}
}

