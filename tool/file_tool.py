# coding:utf-8
def save_to_file(file_name, contents):
    fh = open(file_name, 'w', encoding='utf-8')
    fh.write(contents)
    fh.close()


def string_to_html(msg):
    msg = msg.replace(' ', '&nbsp;')
    msg = msg.replace('\t', '&nbsp;&nbsp;')
    msg = msg.replace('\n', '<BR>')
    return msg


def get_parameter(msg):
    parameters = {}
    status = [0]
    for line in msg:
        if line.startswith('###'):
            status[0] = 1
            msgs = line[3:].split(':')
            if len(msgs) > 2:
                parameters[msgs[0]] = {msgs[1]: msgs[2][:-1]}
        else:
            if status[0]:
                break
    # return json.dumps(parameters, ensure_ascii=False)
    return parameters