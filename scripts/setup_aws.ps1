<#
.SYNOPSIS
Provisions the necessary AWS infrastructure for the ResolveAI API.

.DESCRIPTION
This script uses the AWS CLI to create an ECR repository, an ECS cluster, 
an IAM execution role, a CloudWatch log group, an Application Load Balancer (ALB), 
a Target Group, an ECS Task Definition, and finally an ECS Service.

.NOTES
Requirements: 
- AWS CLI installed and configured (`aws configure`)
- Sufficient IAM permissions to create these resources.
#>

$ErrorActionPreference = "Stop"

# Configuration
$AWS_REGION = "ap-south-1"
$PROJECT_NAME = "resolveai"
$ECR_REPO_NAME = "$PROJECT_NAME-api"
$CLUSTER_NAME = "$PROJECT_NAME-cluster"
$SERVICE_NAME = "$PROJECT_NAME-service"
$TASK_FAMILY = "$PROJECT_NAME-task"
$PORT = 8000

Write-Host "🚀 Starting AWS Infrastructure Setup for $PROJECT_NAME in $AWS_REGION..." -ForegroundColor Cyan

# 1. Create ECR Repository
Write-Host "📦 Creating ECR Repository: $ECR_REPO_NAME..."
try {
    $ecr = aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION 2>$null
    Write-Host "ECR repository already exists." -ForegroundColor Yellow
} catch {
    aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION | Out-Null
    Write-Host "Created ECR repository." -ForegroundColor Green
}

# 2. Create ECS Cluster
Write-Host "🏗️ Creating ECS Cluster: $CLUSTER_NAME..."
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION | Out-Null
Write-Host "Created ECS cluster." -ForegroundColor Green

# 3. Create IAM Execution Role for ECS Tasks
$ROLE_NAME = "${PROJECT_NAME}EcsExecutionRole"
Write-Host "🔑 Creating IAM Role: $ROLE_NAME..."
$trustPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"@

try {
    aws iam get-role --role-name $ROLE_NAME 2>$null | Out-Null
    Write-Host "IAM role already exists." -ForegroundColor Yellow
} catch {
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document $trustPolicy | Out-Null
    aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy | Out-Null
    Write-Host "Created IAM execution role." -ForegroundColor Green
    Start-Sleep -Seconds 10 # Wait for IAM role propagation
}

$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$EXECUTION_ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

# 4. Create CloudWatch Log Group
$LOG_GROUP = "/ecs/$PROJECT_NAME"
Write-Host "📝 Creating CloudWatch Log Group: $LOG_GROUP..."
try {
    aws logs create-log-group --log-group-name $LOG_GROUP --region $AWS_REGION 2>$null
    Write-Host "Created log group." -ForegroundColor Green
} catch {
    Write-Host "Log group already exists." -ForegroundColor Yellow
}

# 5. Create basic VPC resources (Using default VPC for simplicity)
Write-Host "🌐 Retrieving default VPC subnets..."
$VPC_ID = (aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query "Vpcs[0].VpcId" --output text)
$SUBNETS = (aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query "Subnets[*].SubnetId" --output text).Split(" ")

Write-Host "Creating Security Group for ALB and ECS Tasks..."
$SG_NAME = "${PROJECT_NAME}-sg"
try {
    $SG_ID = (aws ec2 describe-security-groups --filters Name=group-name,Values=$SG_NAME --query "SecurityGroups[0].GroupId" --output text)
    if (-not $SG_ID -or $SG_ID -eq "None") { throw "Not found" }
    Write-Host "Security group exists: $SG_ID" -ForegroundColor Yellow
} catch {
    $SG_ID = (aws ec2 create-security-group --group-name $SG_NAME --description "Security group for $PROJECT_NAME" --vpc-id $VPC_ID --query "GroupId" --output text)
    # Allow inbound port 80 (HTTP) for ALB
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 | Out-Null
    # Allow inbound port 8000 for ECS tasks (from ALB)
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --source-group $SG_ID | Out-Null
    Write-Host "Created Security Group: $SG_ID" -ForegroundColor Green
}

# 6. Create Application Load Balancer
Write-Host "⚖️ Creating Load Balancer..."
$ALB_NAME = "${PROJECT_NAME}-alb"
try {
    $ALB_ARN = (aws elbv2 describe-load-balancers --names $ALB_NAME --query "LoadBalancers[0].LoadBalancerArn" --output text 2>$null)
    Write-Host "ALB already exists." -ForegroundColor Yellow
} catch {
    $subnetsJoin = $SUBNETS -join " "
    $ALB_ARN = (aws elbv2 create-load-balancer --name $ALB_NAME --subnets $SUBNETS --security-groups $SG_ID --query "LoadBalancers[0].LoadBalancerArn" --output text)
    Write-Host "Created ALB." -ForegroundColor Green
}

$ALB_DNS = (aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN --query "LoadBalancers[0].DNSName" --output text)

Write-Host "🎯 Creating Target Group..."
$TG_NAME = "${PROJECT_NAME}-tg"
try {
    $TG_ARN = (aws elbv2 describe-target-groups --names $TG_NAME --query "TargetGroups[0].TargetGroupArn" --output text 2>$null)
    Write-Host "Target group already exists." -ForegroundColor Yellow
} catch {
    $TG_ARN = (aws elbv2 create-target-group --name $TG_NAME --protocol HTTP --port $PORT --vpc-id $VPC_ID --target-type ip --health-check-path "/health" --health-check-interval-seconds 30 --query "TargetGroups[0].TargetGroupArn" --output text)
    Write-Host "Created target group." -ForegroundColor Green
}

Write-Host "🎧 Creating ALB Listener..."
try {
    $LISTENER_ARN = (aws elbv2 describe-listeners --load-balancer-arn $ALB_ARN --query "Listeners[0].ListenerArn" --output text 2>$null)
    if (-not $LISTENER_ARN -or $LISTENER_ARN -eq "None") { throw "Not found" }
    Write-Host "Listener already exists." -ForegroundColor Yellow
} catch {
    aws elbv2 create-listener --load-balancer-arn $ALB_ARN --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=$TG_ARN | Out-Null
    Write-Host "Created listener." -ForegroundColor Green
}

# 7. Create Task Definition
Write-Host "📋 Registering ECS Task Definition..."
$TASK_DEF = @"
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "executionRoleArn": "$EXECUTION_ROLE_ARN",
  "taskRoleArn": "$EXECUTION_ROLE_ARN",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "resolveai-api",
      "image": "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest",
      "portMappings": [
        {
          "containerPort": $PORT,
          "hostPort": $PORT,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PORT",
          "value": "8000"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "$LOG_GROUP",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
"@

$TASK_DEF_FILE = "task-def-temp.json"
$TASK_DEF | Out-File -FilePath $TASK_DEF_FILE -Encoding ASCII
aws ecs register-task-definition --cli-input-json file://$TASK_DEF_FILE | Out-Null
Remove-Item $TASK_DEF_FILE
Write-Host "Registered task definition." -ForegroundColor Green

# 8. Create ECS Service
Write-Host "🚀 Creating ECS Service..."
try {
    $serviceStatus = (aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --query "services[0].status" --output text 2>$null)
    if ($serviceStatus -eq "ACTIVE") {
        Write-Host "Service already exists." -ForegroundColor Yellow
    } else {
        throw "Not active"
    }
} catch {
    # Note: the first deployment will fail to run tasks because the image 'latest' doesn't exist yet, 
    # but the service will be created. The GitHub Action will push the image and force-new-deployment.
    $subnetsFormatted = ($SUBNETS | ForEach-Object { "$_" }) -join ","
    aws ecs create-service `
        --cluster $CLUSTER_NAME `
        --service-name $SERVICE_NAME `
        --task-definition $TASK_FAMILY `
        --desired-count 1 `
        --launch-type FARGATE `
        --network-configuration "awsvpcConfiguration={subnets=[$subnetsFormatted],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" `
        --load-balancers "targetGroupArn=$TG_ARN,containerName=resolveai-api,containerPort=$PORT" | Out-Null
    Write-Host "Created ECS Service." -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ AWS Infrastructure Setup Complete!" -ForegroundColor Green
Write-Host "========================================================"
Write-Host "API Load Balancer URL: http://$ALB_DNS" -ForegroundColor Cyan
Write-Host "Note: The API will return 503 until you push the code to GitHub and the GitHub Action deploys the Docker container." -ForegroundColor Yellow
Write-Host "========================================================"
