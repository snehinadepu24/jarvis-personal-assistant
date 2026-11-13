import ast, os, json
root = r'd:\jarvis-personal-assistant'
heavy = {'pandas','numpy','scipy','soundfile','jq','google','google_genai','google_generativeai'}
found = set()
for dirpath, _, files in os.walk(root):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(dirpath, f)
            try:
                tree = ast.parse(open(path, 'r', encoding='utf-8').read())
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        mod = n.name.split('.')[0]
                        if mod in heavy:
                            found.add(mod)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        mod = node.module.split('.')[0]
                        if mod in heavy:
                            found.add(mod)
print(json.dumps(sorted(found)))

