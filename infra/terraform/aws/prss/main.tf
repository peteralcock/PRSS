provider "aws" {
  region = "us-east-1" # Set your AWS region
}

# Networking: VPC and Subnets
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.3.0"
  
  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}

# S3 Bucket for persistent data (e.g., database backups)
resource "aws_s3_bucket" "pr_monitoring_bucket" {
  bucket = "pr-monitoring-bucket"
  acl    = "private"
}

# ECS Cluster
resource "aws_ecs_cluster" "pr_monitoring_cluster" {
  name = "pr-monitoring-cluster"
}

# Elasticache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "pr-monitoring-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis5.0"
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Fargate Task Definition for Web App
resource "aws_ecs_task_definition" "web_app_task" {
  family                   = "pr-monitoring-web-app"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "web"
      image     = "your-dockerhub-username/pr-monitoring-web:latest" # Replace with your Docker image
      essential = true
      portMappings = [{
        containerPort = 5000
        hostPort      = 5000
      }]
      environment = [
        {
          name  = "FLASK_ENV"
          value = "production"
        },
        {
          name  = "DATABASE_URL"
          value = "sqlite:////usr/src/app/pr_monitoring.db" # Or update to RDS URL if needed
        },
        {
          name  = "CELERY_BROKER_URL"
          value = aws_elasticache_cluster.redis.configuration_endpoint_address
        }
      ]
    }
  ])
}

# Fargate Service
resource "aws_ecs_service" "web_app_service" {
  name            = "pr-monitoring-web-service"
  cluster         = aws_ecs_cluster.pr_monitoring_cluster.id
  task_definition = aws_ecs_task_definition.web_app_task.arn
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_service.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.web_target_group.arn
    container_name   = "web"
    container_port   = 5000
  }

  desired_count = 1
}

# Application Load Balancer
resource "aws_lb" "web_lb" {
  name               = "pr-monitoring-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb.id]
  subnets            = module.vpc.public_subnets
}

# Target Group for Web App
resource "aws_lb_target_group" "web_target_group" {
  name     = "pr-monitoring-web-tg"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id

  health_check {
    path = "/"
  }
}

# Listener for ALB
resource "aws_lb_listener" "web_listener" {
  load_balancer_arn = aws_lb.web_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_target_group.arn
  }
}

# Security Groups
resource "aws_security_group" "ecs_service" {
  name        = "ecs-service-sg"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "lb" {
  name        = "lb-sg"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

