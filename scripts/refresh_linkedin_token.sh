#!/bin/bash
exec /usr/local/bin/python3.11 -c "
import sys
sys.path.insert(0, '/home/ubuntu/.hermes/linkedin-poster')
from linkedin_client import LinkedInClient
c = LinkedInClient()
result = c.refresh_access_token()
status = c.get_status()
if result:
    print(f'LinkedIn token refreshed OK. Expires in: {status[\"expires_in_days\"]} days')
    sys.exit(0)
else:
    print(f'LinkedIn token refresh FAILED. Expires in: {status[\"expires_in_days\"]} days')
    sys.exit(1)
"
