variable "finlab_token" {
  description = "token for accessing finlab"
  type        = string
  sensitive   = true
}

variable "tg_token" {
  description = "Database administrator password"
  type        = string
  sensitive   = true
}

variable "loguru_level" {
  description = "log level"
  type        = string
}
