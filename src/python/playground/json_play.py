import json
jason: str ="""
{
   "name": "jamal"
}
"""

# loads from STRING (not file)
data = json.loads(jason)
print(data)  # {'name': 'jamal'}

# dumps from Python object to STRING
json_string = json.dumps(data)
print(json_string)  # '{"name": "jamal"}
