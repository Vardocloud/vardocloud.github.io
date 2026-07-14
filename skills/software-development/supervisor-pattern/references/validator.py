#!/usr/bin/env python3
"""
Supervisor Pattern — JSON Schema + Threshold Validator
Kullanım: 
  python3 validator.py --input result.json --schema '{"required":["field"]}' --threshold '{"min_length":200}'
  python3 validator.py --file /path/to/results.json  # batch mode
"""
import json, sys, argparse

def validate_schema(data, schema):
    """JSON schema validator — jsonsuz çalışır, saf Python."""
    errors = []
    
    if schema.get("type") == "object" and not isinstance(data, dict):
        errors.append(f"Tip: object bekleniyor, {type(data).__name__} geldi")
        return errors
    
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"Eksik: '{field}'")
        elif data[field] is None or data[field] == "" or data[field] == []:
            errors.append(f"Boş: '{field}'")
    
    for prop, rules in schema.get("properties", {}).items():
        if prop not in data:
            continue
        val = data[prop]
        if rules.get("type") == "array":
            if not isinstance(val, list):
                errors.append(f"'{prop}' array olmalı, {type(val).__name__} geldi")
            elif rules.get("minItems") and len(val) < rules["minItems"]:
                errors.append(f"'{prop}' yetersiz: {len(val)} (min: {rules['minItems']})")
        elif rules.get("type") == "number" and isinstance(val, (int, float)):
            if rules.get("minimum") and val < rules["minimum"]:
                errors.append(f"'{prop}' düşük: {val} (min: {rules['minimum']})")
        elif rules.get("type") == "string" and isinstance(val, str):
            if rules.get("minLength") and len(val) < rules["minLength"]:
                errors.append(f"'{prop}' kısa: {len(val)} (min: {rules['minLength']})")
    
    return errors


def check_threshold(data, raw_text, threshold):
    errors = []
    text = raw_text or json.dumps(data, ensure_ascii=False)
    
    if len(text) < threshold.get("min_length", 0):
        errors.append(f"İçerik kısa: {len(text)}c (min: {threshold['min_length']}c)")
    
    for kw in threshold.get("keywords", []):
        if kw.lower() not in text.lower():
            errors.append(f"Keyword eksik: '{kw}'")
    
    return errors


def main():
    parser = argparse.ArgumentParser(description="Supervisor Pattern Validator")
    parser.add_argument("--input", help="JSON string to validate")
    parser.add_argument("--file", help="JSON file path to validate")
    parser.add_argument("--schema", default='{"required":["sources","findings"]}', help="JSON schema")
    parser.add_argument("--threshold", default='{"min_length":100,"keywords":[]}', help="Quality threshold")
    args = parser.parse_args()
    
    # Load input
    if args.file:
        with open(args.file) as f:
            data = json.load(f)
    elif args.input:
        data = json.loads(args.input)
    else:
        data = json.load(sys.stdin)
    
    schema = json.loads(args.schema)
    threshold = json.loads(args.threshold)
    
    # Validate
    schema_errors = validate_schema(data, schema)
    threshold_errors = check_threshold(data, "", threshold)
    
    all_errors = schema_errors + threshold_errors
    status = "passed" if not all_errors else "failed"
    
    result = {
        "status": status,
        "schema_errors": schema_errors,
        "threshold_errors": threshold_errors,
        "all_errors": all_errors,
        "retry_needed": status == "failed"
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
