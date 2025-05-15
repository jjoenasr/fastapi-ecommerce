from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	app_name: str = 'Awesome API'
	app_version: str = '0.1.0'
	app_description: str = 'Awesome API for awesome things'
	supabase_url: str
	supabase_key: str
	supabase_bucket_url: str
	stripe_key: str
	stripe_endpoint_secret: str
	db_host: str
	db_user: str
	db_password: str
	allowed_hosts: list[str] = ['localhost', 'aws-0-eu-central-1.pooler.supabase.com']

	model_config = SettingsConfigDict(env_file=".env")

settings = Settings()