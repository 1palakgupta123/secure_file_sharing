from utils import create_access_token
from datetime import timedelta

data = {"sub": "testuser"}
token = create_access_token(data, expires_delta=timedelta(minutes=30))
print(token)  