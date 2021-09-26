def get_class_docs(class_: classmethod, target_methods=None):
    def parse_doc(text: str):
        if text is None or len(text) == 0:
            return None
        lines = text.split('\n')
        if lines[0] == '':
            lines = lines[1:]
        if lines[-1] == '' or lines[-1].startswith('    '):
            lines = lines[:-1]
        res = ''
        for li in lines:
            while li.startswith(' '):
                li = li[1:]
            res = res + li + '\n'
        res = res[:-1]
        return res

    if target_methods is None:
        target_methods = [
            'get', 'post', 'put', 'delete'
        ]
    dirs = dir(class_)
    result = {
        'disc': parse_doc(class_.__doc__),
        'methods': {}
    }
    for d in dirs:
        if d not in target_methods:
            continue
        target = eval(f"class_.{d}")
        if type(target) is not None and '__doc__' in dir(target):
            doc = parse_doc(target.__doc__)
            if doc is None:
                continue
            result['methods'][d] = doc
    return result
