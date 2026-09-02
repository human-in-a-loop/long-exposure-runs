import ast, pathlib
tree = ast.parse(pathlib.Path('scripts/palette_render/render_stem.py').read_text())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'render_stem':
        args = node.args
        posonly = [a.arg for a in args.posonlyargs]
        pos = [a.arg for a in args.args]
        kwonly = [a.arg for a in args.kwonlyargs]
        kwdefaults = args.kw_defaults
        print('render_stem signature:')
        print(f'  posonlyargs: {posonly}')
        print(f'  args: {pos}')
        print(f'  kwonlyargs: {kwonly}')
        for name, default in zip(kwonly, kwdefaults):
            defstr = ast.unparse(default) if default else 'NO_DEFAULT'
            print(f'    {name} default: {defstr}')
        print(f'  vararg: {args.vararg.arg if args.vararg else None}')
        break
