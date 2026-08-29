import ast
src = open('scripts/ear/leak_test.py').read()
tree = ast.parse(src)
bad = []
for n in ast.walk(tree):
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'max':
        arg_names = [a.id for a in n.args if isinstance(a, ast.Name)]
        if 'S_model' in arg_names and 'S_resid' in arg_names:
            bad.append(ast.dump(n))
print('bad_calls:', bad)
found = any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'STATISTIC_VERSION' for t in n.targets) for n in ast.walk(tree))
print('statistic_version_assign_found:', found)
fn_found = any(isinstance(n, ast.FunctionDef) and n.name == 'f1_pooled_variance_statistic' for n in ast.walk(tree))
print('f1_pooled_variance_statistic_defined:', fn_found)
import subprocess, sys
r = subprocess.run([sys.executable, '-c', 'import scripts.ear.leak_test as m; print("import ok; fn=", type(m.f1_pooled_variance_statistic).__name__, "STATISTIC_VERSION=", m.STATISTIC_VERSION)'], capture_output=True, text=True)
print('IMPORT_STDOUT:', r.stdout)
print('IMPORT_STDERR:', r.stderr)
