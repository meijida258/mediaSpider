from django.test import TestCase
from django.contrib.auth.hashers import make_password
# Create your tests here.
print(make_password(123456, None,'pbkdf2_sha256'))