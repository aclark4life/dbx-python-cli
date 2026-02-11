# {{ project_name }} settings module.
# Import all base settings and add project-specific configurations here.

from .base import *  # noqa

# Add project-specific settings below
# Example:
# DEBUG = False
# ALLOWED_HOSTS = ['example.com']

# Add project-specific apps to INSTALLED_APPS
INSTALLED_APPS = (
    INSTALLED_APPS  # noqa: F405
    + [
        # Add your project-specific apps here
        # Example:
        # "myapp",
    ]
)

# Queryable Encryption (QE) Configuration
# Uncomment and configure these settings to enable Queryable Encryption.
# See: https://django-mongodb-backend.readthedocs.io/en/latest/howto/queryable-encryption/
#
# Requirements:
# - MongoDB 7.0+ (replica set or sharded cluster)
# - pip install 'django-mongodb-backend[encryption]'
# - Download Automatic Encryption Shared Library from MongoDB
#
# from pymongo.encryption_options import AutoEncryptionOpts
#
# DATABASES = {
#     "default": {
#         "ENGINE": "django_mongodb_backend",
#         "HOST": os.getenv("MONGODB_URI", "mongodb+srv://cluster0.example.mongodb.net"),  # noqa: F405
#         "NAME": "{{ project_name }}",
#     },
#     # Encrypted database connection with AutoEncryptionOpts
#     "encrypted": {
#         "ENGINE": "django_mongodb_backend",
#         "HOST": os.getenv("MONGODB_URI", "mongodb+srv://cluster0.example.mongodb.net"),  # noqa: F405
#         "NAME": "{{ project_name }}_encrypted",
#         "OPTIONS": {
#             "auto_encryption_opts": AutoEncryptionOpts(
#                 key_vault_namespace="{{ project_name }}_encrypted.__keyVault",
#                 kms_providers={
#                     # Local KMS provider (for development only)
#                     "local": {
#                         # Generate with: os.urandom(96)
#                         "key": b"REPLACE_WITH_96_BYTE_KEY",
#                     },
#                     # For production, use a KMS provider like AWS:
#                     # "aws": {
#                     #     "accessKeyId": os.getenv("AWS_ACCESS_KEY_ID"),  # noqa: F405
#                     #     "secretAccessKey": os.getenv("AWS_SECRET_ACCESS_KEY"),  # noqa: F405
#                     # },
#                 },
#                 # Path to mongo_crypt_v1.so (Linux), mongo_crypt_v1.dylib (macOS),
#                 # or mongo_crypt_v1.dll (Windows)
#                 crypt_shared_lib_path="/path/to/mongo_crypt_v1.so",
#                 crypt_shared_lib_required=True,
#                 # In production, add encrypted_fields_map from showencryptedfieldsmap
#                 # encrypted_fields_map=json_util.loads("""..."""),
#             )
#         },
#         # For production KMS (e.g., AWS):
#         # "KMS_CREDENTIALS": {
#         #     "aws": {
#         #         "key": "arn:aws:kms:...",  # Amazon Resource Name
#         #         "region": "us-east-1",
#         #     },
#         # },
#     },
# }
#
# # Database router for encrypted models
# DATABASE_ROUTERS = [
#     "django_mongodb_backend.routers.MongoRouter",
#     # Add your custom router for encrypted models:
#     # "myapp.routers.EncryptedRouter",
# ]
#
# # Example encrypted model router (create in myapp/routers.py):
# # class EncryptedRouter:
# #     def allow_migrate(self, db, app_label, model_name=None, **hints):
# #         if app_label == "myapp":
# #             return db == "encrypted"
# #         if db == "encrypted":
# #             return False
# #         return None
# #
# #     def db_for_read(self, model, **hints):
# #         if model._meta.app_label == "myapp":
# #             return "encrypted"
# #         return None
# #
# #     db_for_write = db_for_read
#
# # After configuring, run:
# # python manage.py migrate --database encrypted
# # python manage.py showencryptedfieldsmap --database encrypted
