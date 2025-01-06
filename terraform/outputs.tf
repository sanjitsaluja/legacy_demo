output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.data_lake_bucket.id
}

output "glue_database_name" {
  description = "Name of the Glue catalog database"
  value       = aws_glue_catalog_database.iceberg_db.name
}

output "iam_role_arn" {
  description = "ARN of the IAM role for data lake access"
  value       = aws_iam_role.data_lake_iam_role.arn
}
