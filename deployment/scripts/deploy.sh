#!/bin/bash
# PowerAutomation v0.571 自动化部署脚本
# 完整的AWS基础设施和应用部署

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
CONFIG_DIR="$PROJECT_ROOT/configs"

# 默认配置
AWS_REGION="${AWS_REGION:-us-east-1}"
ENVIRONMENT="${ENVIRONMENT:-production}"
PROJECT_NAME="powerautomation"
VERSION="v0.571"

# 检查必要的工具
check_prerequisites() {
    log_info "检查部署前置条件..."
    
    local missing_tools=()
    
    # 检查AWS CLI
    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws-cli")
    fi
    
    # 检查Terraform
    if ! command -v terraform &> /dev/null; then
        missing_tools+=("terraform")
    fi
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    # 检查jq
    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("python3")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必要工具: ${missing_tools[*]}"
        log_info "请安装缺少的工具后重新运行"
        exit 1
    fi
    
    # 检查AWS凭证
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS凭证未配置或无效"
        log_info "请运行 'aws configure' 配置AWS凭证"
        exit 1
    fi
    
    log_success "前置条件检查通过"
}

# 初始化Terraform后端
init_terraform_backend() {
    log_info "初始化Terraform后端..."
    
    local state_bucket="${PROJECT_NAME}-terraform-state-${AWS_REGION}"
    local lock_table="${PROJECT_NAME}-terraform-locks"
    
    # 检查S3存储桶是否存在
    if ! aws s3api head-bucket --bucket "$state_bucket" 2>/dev/null; then
        log_info "创建Terraform状态存储桶: $state_bucket"
        aws s3api create-bucket \
            --bucket "$state_bucket" \
            --region "$AWS_REGION" \
            --create-bucket-configuration LocationConstraint="$AWS_REGION" 2>/dev/null || true
        
        # 启用版本控制
        aws s3api put-bucket-versioning \
            --bucket "$state_bucket" \
            --versioning-configuration Status=Enabled
        
        # 启用服务器端加密
        aws s3api put-bucket-encryption \
            --bucket "$state_bucket" \
            --server-side-encryption-configuration '{
                "Rules": [{
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }]
            }'
    fi
    
    # 检查DynamoDB表是否存在
    if ! aws dynamodb describe-table --table-name "$lock_table" &>/dev/null; then
        log_info "创建Terraform锁定表: $lock_table"
        aws dynamodb create-table \
            --table-name "$lock_table" \
            --attribute-definitions AttributeName=LockID,AttributeType=S \
            --key-schema AttributeName=LockID,KeyType=HASH \
            --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
            --region "$AWS_REGION"
        
        # 等待表创建完成
        aws dynamodb wait table-exists --table-name "$lock_table" --region "$AWS_REGION"
    fi
    
    log_success "Terraform后端初始化完成"
}

# 构建Docker镜像
build_docker_images() {
    log_info "构建PowerAutomation Docker镜像..."
    
    local ecr_registry=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION}.amazonaws.com
    
    # 登录ECR
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ecr_registry"
    
    # 创建ECR仓库（如果不存在）
    local repositories=("powerautomation/enterprise" "powerautomation/personal-pro" "powerautomation/kilo-code")
    
    for repo in "${repositories[@]}"; do
        if ! aws ecr describe-repositories --repository-names "$repo" &>/dev/null; then
            log_info "创建ECR仓库: $repo"
            aws ecr create-repository --repository-name "$repo" --region "$AWS_REGION"
        fi
    done
    
    # 构建企业版镜像
    log_info "构建企业版镜像..."
    docker build -t "$ecr_registry/powerautomation/enterprise:$VERSION" \
        -f "$PROJECT_ROOT/docker/Dockerfile.enterprise" \
        "$PROJECT_ROOT"
    
    docker push "$ecr_registry/powerautomation/enterprise:$VERSION"
    
    # 构建个人专业版镜像
    log_info "构建个人专业版镜像..."
    docker build -t "$ecr_registry/powerautomation/personal-pro:$VERSION" \
        -f "$PROJECT_ROOT/docker/Dockerfile.personal-pro" \
        "$PROJECT_ROOT"
    
    docker push "$ecr_registry/powerautomation/personal-pro:$VERSION"
    
    # 构建Kilo Code引擎镜像
    log_info "构建Kilo Code引擎镜像..."
    docker build -t "$ecr_registry/powerautomation/kilo-code:$VERSION" \
        -f "$PROJECT_ROOT/docker/Dockerfile.kilo-code" \
        "$PROJECT_ROOT"
    
    docker push "$ecr_registry/powerautomation/kilo-code:$VERSION"
    
    log_success "Docker镜像构建和推送完成"
}

# 部署基础设施
deploy_infrastructure() {
    log_info "部署PowerAutomation基础设施..."
    
    cd "$TERRAFORM_DIR"
    
    # 初始化Terraform
    terraform init
    
    # 验证配置
    terraform validate
    
    # 规划部署
    log_info "生成Terraform执行计划..."
    terraform plan \
        -var="aws_region=$AWS_REGION" \
        -var="environment=$ENVIRONMENT" \
        -var="database_password=$(openssl rand -base64 32)" \
        -out=tfplan
    
    # 应用部署
    log_info "应用基础设施变更..."
    terraform apply tfplan
    
    # 保存输出
    terraform output -json > "$CONFIG_DIR/terraform-outputs.json"
    
    log_success "基础设施部署完成"
}

# 部署应用服务
deploy_application() {
    log_info "部署PowerAutomation应用服务..."
    
    # 读取Terraform输出
    local terraform_outputs="$CONFIG_DIR/terraform-outputs.json"
    
    if [ ! -f "$terraform_outputs" ]; then
        log_error "Terraform输出文件不存在: $terraform_outputs"
        exit 1
    fi
    
    local cluster_name=$(jq -r '.ecs_cluster_name.value' "$terraform_outputs")
    local vpc_id=$(jq -r '.vpc_id.value' "$terraform_outputs")
    local private_subnets=$(jq -r '.private_subnet_ids.value[]' "$terraform_outputs" | tr '\n' ',' | sed 's/,$//')
    local security_group=$(jq -r '.ecs_security_group_id.value' "$terraform_outputs")
    
    # 更新ECS服务
    log_info "更新ECS服务..."
    
    # 企业版服务
    aws ecs update-service \
        --cluster "$cluster_name" \
        --service "powerauto-enterprise" \
        --force-new-deployment \
        --region "$AWS_REGION"
    
    # 个人专业版服务
    aws ecs update-service \
        --cluster "$cluster_name" \
        --service "powerauto-personal-pro" \
        --force-new-deployment \
        --region "$AWS_REGION"
    
    # Kilo Code引擎服务
    aws ecs update-service \
        --cluster "$cluster_name" \
        --service "powerauto-kilo-code" \
        --force-new-deployment \
        --region "$AWS_REGION"
    
    # 等待服务稳定
    log_info "等待服务部署完成..."
    aws ecs wait services-stable \
        --cluster "$cluster_name" \
        --services "powerauto-enterprise" "powerauto-personal-pro" "powerauto-kilo-code" \
        --region "$AWS_REGION"
    
    log_success "应用服务部署完成"
}

# 部署Lambda函数
deploy_lambda_functions() {
    log_info "部署Lambda函数..."
    
    local lambda_dir="$PROJECT_ROOT/lambda"
    
    # 打包Lambda函数
    cd "$lambda_dir"
    
    # 录制数据处理函数
    log_info "部署录制数据处理函数..."
    zip -r recording-processor.zip recording_processor/
    
    aws lambda update-function-code \
        --function-name "powerauto-recording-processor" \
        --zip-file fileb://recording-processor.zip \
        --region "$AWS_REGION" || \
    aws lambda create-function \
        --function-name "powerauto-recording-processor" \
        --runtime python3.9 \
        --role "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role" \
        --handler "recording_processor.lambda_handler" \
        --zip-file fileb://recording-processor.zip \
        --timeout 300 \
        --memory-size 1024 \
        --region "$AWS_REGION"
    
    # Kilo Code分析函数
    log_info "部署Kilo Code分析函数..."
    zip -r kilo-code-analyzer.zip kilo_code_analyzer/
    
    aws lambda update-function-code \
        --function-name "powerauto-kilo-code-analyzer" \
        --zip-file fileb://kilo-code-analyzer.zip \
        --region "$AWS_REGION" || \
    aws lambda create-function \
        --function-name "powerauto-kilo-code-analyzer" \
        --runtime python3.9 \
        --role "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role" \
        --handler "kilo_code_analyzer.lambda_handler" \
        --zip-file fileb://kilo-code-analyzer.zip \
        --timeout 900 \
        --memory-size 3008 \
        --region "$AWS_REGION"
    
    log_success "Lambda函数部署完成"
}

# 配置监控和告警
setup_monitoring() {
    log_info "配置监控和告警..."
    
    # 创建CloudWatch仪表板
    local dashboard_body=$(cat "$CONFIG_DIR/cloudwatch-dashboard.json")
    
    aws cloudwatch put-dashboard \
        --dashboard-name "PowerAutomation-v0571" \
        --dashboard-body "$dashboard_body" \
        --region "$AWS_REGION"
    
    # 创建告警
    log_info "创建CloudWatch告警..."
    
    # ECS CPU使用率告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "PowerAuto-ECS-HighCPU" \
        --alarm-description "ECS CPU使用率过高" \
        --metric-name CPUUtilization \
        --namespace AWS/ECS \
        --statistic Average \
        --period 300 \
        --threshold 80 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2 \
        --alarm-actions "arn:aws:sns:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):powerauto-alerts" \
        --dimensions Name=ServiceName,Value=powerauto-enterprise Name=ClusterName,Value=powerauto-cluster \
        --region "$AWS_REGION"
    
    # RDS连接数告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "PowerAuto-RDS-HighConnections" \
        --alarm-description "RDS连接数过高" \
        --metric-name DatabaseConnections \
        --namespace AWS/RDS \
        --statistic Average \
        --period 300 \
        --threshold 80 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2 \
        --alarm-actions "arn:aws:sns:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):powerauto-alerts" \
        --dimensions Name=DBInstanceIdentifier,Value=powerauto-production \
        --region "$AWS_REGION"
    
    log_success "监控和告警配置完成"
}

# 运行部署后测试
run_post_deployment_tests() {
    log_info "运行部署后测试..."
    
    # 读取部署输出
    local terraform_outputs="$CONFIG_DIR/terraform-outputs.json"
    local alb_dns=$(jq -r '.alb_dns_name.value' "$terraform_outputs")
    local api_url=$(jq -r '.api_gateway_url.value' "$terraform_outputs")
    
    # 健康检查
    log_info "执行健康检查..."
    
    # 检查ALB健康状态
    local health_check_url="https://$alb_dns/health"
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$health_check_url" > /dev/null; then
            log_success "ALB健康检查通过"
            break
        fi
        
        log_info "等待服务启动... ($attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "ALB健康检查失败"
        return 1
    fi
    
    # 检查API Gateway
    if curl -f -s "$api_url/health" > /dev/null; then
        log_success "API Gateway健康检查通过"
    else
        log_warning "API Gateway健康检查失败"
    fi
    
    # 运行自动化测试
    log_info "运行自动化测试套件..."
    python3 "$PROJECT_ROOT/tests/automated_testing_framework/system_tester.py" \
        --environment production \
        --endpoint "https://$alb_dns"
    
    log_success "部署后测试完成"
}

# 生成部署报告
generate_deployment_report() {
    log_info "生成部署报告..."
    
    local report_file="$CONFIG_DIR/deployment-report-$(date +%Y%m%d-%H%M%S).json"
    local terraform_outputs="$CONFIG_DIR/terraform-outputs.json"
    
    # 收集部署信息
    local deployment_info=$(cat << EOF
{
    "deployment": {
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "version": "$VERSION",
        "environment": "$ENVIRONMENT",
        "region": "$AWS_REGION",
        "deployer": "$(aws sts get-caller-identity --query Arn --output text)"
    },
    "infrastructure": $(cat "$terraform_outputs"),
    "services": {
        "ecs_cluster": "$(jq -r '.ecs_cluster_name.value' "$terraform_outputs")",
        "database": "$(jq -r '.rds_endpoint.value' "$terraform_outputs")",
        "cache": "$(jq -r '.redis_endpoint.value' "$terraform_outputs")",
        "load_balancer": "$(jq -r '.alb_dns_name.value' "$terraform_outputs")",
        "api_gateway": "$(jq -r '.api_gateway_url.value' "$terraform_outputs")",
        "cloudfront": "$(jq -r '.cloudfront_domain_name.value' "$terraform_outputs")"
    },
    "status": "completed"
}
EOF
    )
    
    echo "$deployment_info" | jq '.' > "$report_file"
    
    log_success "部署报告已生成: $report_file"
    
    # 显示关键信息
    echo
    log_info "=== PowerAutomation v0.571 部署完成 ==="
    echo "🌐 Web访问地址: https://$(jq -r '.cloudfront_domain_name.value' "$terraform_outputs")"
    echo "🔗 API Gateway: $(jq -r '.api_gateway_url.value' "$terraform_outputs")"
    echo "⚖️  负载均衡器: $(jq -r '.alb_dns_name.value' "$terraform_outputs")"
    echo "🗄️  数据库端点: $(jq -r '.rds_endpoint.value' "$terraform_outputs")"
    echo "📊 监控仪表板: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:name=PowerAutomation-v0571"
    echo
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    rm -f "$TERRAFORM_DIR/tfplan"
    rm -f "$PROJECT_ROOT/lambda"/*.zip
}

# 主函数
main() {
    log_info "开始PowerAutomation v0.571自动化部署"
    echo "环境: $ENVIRONMENT"
    echo "区域: $AWS_REGION"
    echo "版本: $VERSION"
    echo
    
    # 设置错误处理
    trap cleanup EXIT
    
    # 执行部署步骤
    check_prerequisites
    init_terraform_backend
    build_docker_images
    deploy_infrastructure
    deploy_application
    deploy_lambda_functions
    setup_monitoring
    run_post_deployment_tests
    generate_deployment_report
    
    log_success "PowerAutomation v0.571部署成功完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

