


def update_build(build_path, jar_content):
    end_count = jar_content.rfind('/')
    jar_name = jar_content[end_count + 1:]

    # 读写目前的build.xml文件进行追加操作！
    build_f = open(build_path)
    build_content = build_f.readlines()
    build_f.close()
    path_line = 0
    for content in build_content:
        if '</path>' in content:
            path_line = build_content.index(content)
    if path_line != 0:
        print('in')
        build_w = open(build_path, 'w')
        build_content.insert(path_line,
                             '        <pathelement location="webapps/WEB-INF/lib/'+jar_name[:-1]+'"/>\n')
        build_w.writelines(build_content)
        build_w.close()

