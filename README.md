# crawler findmind

export requirements.txt before terraform apply:

`poetry export -f requirements.txt --output requirements.txt --without-hashes`

terraform apply:

`terraform apply -replace=google_cloudfunctions2_function.function -replace=google_cloud_scheduler_job.job -var-file=secret.tfvars -auto-approve`

`terraform destroy -var-file=secret.tfvars -auto-approve`
