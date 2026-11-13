import ast, os, re, sys
root = r'd:\jarvis-personal-assistant'
heavy_patterns = [r'^\s*import\s+(pandas|numpy|scipy|soundfile|jq|google)',
                  r'^\s*from\s+google\..* import',
                  r'^\s*from\s+(pandas|numpy|scipy|soundfile|jq) import']
regexes = [re.compile(p) for p in heavy_patterns]
for dirpath, _, files in os.walk(root):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(dirpath, f)
            with open(path, 'r', encoding='utf-8') as fh:
                lines = fh.readlines()
            new_lines = []
            changed = False
            for line in lines:
                if any(r.match(line) for r in regexes):
                    changed = True
                    continue  # drop the line
                new_lines.append(line)
            if changed:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.writelines(new_lines)
                print(f'Cleaned {path}')

