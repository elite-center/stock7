locals {
  project = "stock7707"
}

provider "google" {
  project = "stock7707"
  region  = "us-central1"
}

data "google_compute_default_service_account" "default" {
}

data "archive_file" "source" {
  type        = "zip"
  source_dir  = "../src/crawler-finlab"
  output_path = "/tmp/finlab-source.zip"
}

resource "google_storage_bucket" "bucket" {
  name                        = "${local.project}-gcf-source"
  location                    = "US"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "object" {
  name   = "finlab-source.zip"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.source.output_path
}

resource "google_cloudfunctions2_function" "function" {
  name        = "finlab"
  location    = "us-central1"
  description = "finlab crawler"

  build_config {
    runtime     = "python310"
    entry_point = "main"
    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "512M"
    timeout_seconds    = 60
    ingress_settings   = "ALLOW_ALL"
    environment_variables = {
      FINLAB_TOKEN = var.finlab_token
      TG_TOKEN     = var.tg_token
      LOGURU_LEVEL = var.loguru_level
    }
  }
}

output "function_uri" {
  value = google_cloudfunctions2_function.function.service_config[0].uri
}


resource "google_cloud_scheduler_job" "job" {
  project          = local.project
  region           = google_cloudfunctions2_function.function.location
  name             = "finmind"
  description      = "finmind"
  schedule         = "0 0,10 * * *"
  time_zone        = "UTC"
  attempt_deadline = "320s"

  retry_config {
    retry_count = 3
  }

  http_target {
    http_method = "GET"
    uri         = google_cloudfunctions2_function.function.service_config[0].uri

    oidc_token {
      service_account_email = data.google_compute_default_service_account.default.email
    }
  }
}

