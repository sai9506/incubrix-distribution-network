
import json

from app.main import app

openapi_schema = app.openapi()

with open("openapi.yaml", "w", encoding="utf-8") as file:
    json.dump(openapi_schema, file, indent=2)

print("OpenAPI specification generated successfully!")
print("OpenAPI version:", openapi_schema.get("openapi"))
print("Available API paths:")

for path in openapi_schema.get("paths", {}):
    print(path)
