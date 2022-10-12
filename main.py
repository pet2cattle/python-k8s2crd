import pureyaml
import sys
import os

def add_element(key, value, depth, output):
  spaces = 12 + depth*2

  if type(value) is str or type(value) is bool or type(value) is int:

    for _ in range(0, spaces):
      output += ' '
    output += key+':\n'
    for _ in range(0, spaces):
      output += ' '

    if type(value) is str:
      actual_type = 'string'
    elif type(value) is bool:
      actual_type = 'boolean'
    elif type(value) is int:
      actual_type = 'integer'

    output += '  type: '+actual_type+'\n'
  else:
    for _ in range(0, spaces):
      output += ' '
    output += key+':\n'
    for _ in range(0, spaces):
      output += ' '

    if type(value) is dict:
      output += '  type: object\n'
      for _ in range(0, spaces):
        output += ' '
      output += '  properties:\n'
      for inner_key in value:
        output = add_element(inner_key, value[inner_key], depth+2, output)
    elif type(value) is list:
      output += '  type: array\n'
      for _ in range(0, spaces):
        output += ' '
      output += '  items:\n'
      if type(value[0]) is str or type(value[0]) is bool or type(value[0]) is int:
        if type(value[0]) is str:
          actual_type = 'string'
        elif type(value[0]) is bool:
          actual_type = 'boolean'
        elif type(value[0]) is int:
          actual_type = 'integer'

        for _ in range(0, spaces):
          output += ' '

        output += '    type: '+actual_type+'\n'
      else:
        for inner_key in value:
          output = add_element(inner_key, value[inner_key], depth+2, output)
    else:
      sys.exit("Error parsing object - unexpected value: "+str(value)+" ("+str(type(value))+")")

  return output

try:
  # pyodine compatibility
  if sys.argv[0]:
    input_str = sys.stdin.read() + "\n"
  
  input = pureyaml.loads(input_str)

except Exception as e:
  output = ""
  exc_type, exc_obj, exc_tb = sys.exc_info()
  fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
  print(exc_type, fname, exc_tb.tb_lineno)
  sys.exit("Error: "+str(e))

if len(sys.argv) != 2:
  candidate_ag_w_ver = input['apiVersion']
else:
  candidate_ag_w_ver = sys.argv[1]

tk_apigroup =candidate_ag_w_ver.split('/')

if len(tk_apigroup)>1:
  api_group=tk_apigroup[0]
  api_version=tk_apigroup[1]
else:
  api_group=tk_apigroup[0]
  api_version="v1"

output = """apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
name: """+input['kind'].lower()+"""s."""+api_group+"""
spec:
group: """+api_group+"""
names:
  kind: """+input['kind']+"""
  plural: """+input['kind'].lower()+"""s
scope: Namespaced
versions:
- name: """+api_version+"""
  served: true
  storage: true
  schema:
    openAPIV3Schema:
      type: object"""
found_element = False
depth = 0
for key in input:
  if key in [ 'status', 'apiVersion', 'kind', 'metadata']:
    continue
  if key == "spec":
    input[key].pop('finalizers', None)

  if type(input[key]) is dict and len(input[key].keys()) == 0:
    continue

  if not found_element:
    found_element = True
    output += """
      properties:
"""
  output = add_element(key, input[key], depth, output)

print(output)

