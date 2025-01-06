provider "aws" {
  region = var.aws_region
}

# S3 Bucket for the Data Lake
resource "aws_s3_bucket" "data_lake_bucket" {
  bucket        = "mental-health-data-lake" # Change to your unique bucket name
  force_destroy = true

  tags = {
    Name        = "Mental Health Data Lake"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_acl" "data_lake_acl" {
  bucket = aws_s3_bucket.data_lake_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake_encryption" {
  bucket = aws_s3_bucket.data_lake_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "data_lake_versioning" {
  bucket = aws_s3_bucket.data_lake_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Policy to Allow Glue and Compute Access
resource "aws_s3_bucket_policy" "data_lake_policy" {
  bucket = aws_s3_bucket.data_lake_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "AllowGlueAccess"
        Effect    = "Allow"
        Principal = { Service = "glue.amazonaws.com" }
        Action    = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
        Resource  = [
          "${aws_s3_bucket.data_lake_bucket.arn}",
          "${aws_s3_bucket.data_lake_bucket.arn}/*"
        ]
      }
    ]
  })
}

# Glue Catalog for Iceberg Metadata
resource "aws_glue_catalog_database" "iceberg_db" {
  name = "mental_health_data"
}

# IAM Role for Glue and Compute Resources
resource "aws_iam_role" "data_lake_iam_role" {
  name = "DataLakeAccessRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          Service = "glue.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Fetch Account ID Dynamically
data "aws_caller_identity" "current" {}

# IAM Policy for S3 and Glue Access
resource "aws_iam_policy" "data_lake_policy" {
  name        = "DataLakeAccessPolicy"
  description = "Policy for accessing S3 bucket and Glue catalog for Iceberg"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Action    = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ],
        Resource = [
          "${aws_s3_bucket.data_lake_bucket.arn}",
          "${aws_s3_bucket.data_lake_bucket.arn}/*"
        ]
      },
      {
        Effect    = "Allow",
        Action    = [
          "glue:CreateTable",
          "glue:GetTable",
          "glue:DeleteTable",
          "glue:UpdateTable"
        ],
        Resource = "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:database/mental_health_data"
      }
    ]
  })
}

# Attach Policy to IAM Role
resource "aws_iam_role_policy_attachment" "data_lake_policy_attachment" {
  role       = aws_iam_role.data_lake_iam_role.name
  policy_arn = aws_iam_policy.data_lake_policy.arn
}

