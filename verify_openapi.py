#!/usr/bin/env python3
import urllib.request
import json

data = json.loads(urllib.request.urlopen('http://localhost:8000/openapi.json').read())

print("\n===== POST /ingestions Parameters =====")
params = data['paths']['/ingestions']['post']['parameters']
for p in params:
    schema = p.get('schema', {})
    if 'allOf' in schema:
        ref = schema['allOf'][0].get('$ref', '')
        print(f"{p['name']}: {ref}")
    else:
        print(f"{p['name']}: {schema.get('type', 'object')}")

print("\n===== GET /ingestions Parameters =====")
params = data['paths']['/ingestions']['get']['parameters']
for p in params:
    schema = p.get('schema', {})
    if 'anyOf' in schema:
        ref = schema['anyOf'][0].get('$ref', '')
        print(f"{p['name']}: {ref}")
    else:
        print(f"{p['name']}: {schema.get('type', 'object')}")

print("\n===== Checking for Portuguese enum names in all components =====")
portuguese_enums = ['FonteIngestao', 'MetodoIngestao', 'StatusIngestao']
found = False
for schema_name in data['components']['schemas']:
    if any(enum_name in schema_name for enum_name in portuguese_enums):
        print(f"FOUND PORTUGUESE ENUM: {schema_name}")
        found = True

if not found:
    print("✅ NO PORTUGUESE ENUM NAMES FOUND - ALL ENGLISH!")

print("\n===== English Enum Component Names =====")
english_enums = ['IngestionSource', 'IngestionMethod', 'IngestionStatus']
for enum_name in english_enums:
    if enum_name in data['components']['schemas']:
        print(f"✅ {enum_name}")
    else:
        print(f"❌ {enum_name} NOT FOUND")
