#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert yml to sql. Support Mysql5.6+
"""
import yaml

table_list = ['装备表', '项目表', '摄像头表', '推荐表', '投诉表', '测试表', '提现表']
template_table = '''
CREATE TABLE `{table_name}` (
{field_list_str}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{table_comment}';
'''
template_field = '`{field_name}` {field_type}{field_size} {field_notnull} {field_default} {field_comment},\n'
field_type_dict = {
    'integer': 'int',
    'decimal': 'float',
    'string': 'varchar',
    'text': 'text',
    'timestamp': 'timestamp'
}


def parse(table_name):
    with open('../db/' + table_name + '.yml', 'r', encoding='utf-8') as stream:
        data = yaml.load(stream)
    # print(data)
    assert isinstance(data, dict)

    field_list_str = ''
    for field_name, field_attr in data['field'].items():
        # print(field_name, field_attr)
        field_type = field_type_dict[field_attr['type']]
        if field_type == 'int' and field_attr['size'] == 1:
            # boolean type
            field_type = 'tinyint'

        field_scale = ',' + str(field_attr['scale']) \
            if field_attr['type'] == 'decimal' and 'scale' in field_attr else ''
        field_size = '(' + str(field_attr['size']) + field_scale + ')' \
            if field_attr['type'] not in ['text', 'timestamp'] and 'size' in field_attr else ''

        field_notnull = 'NOT NULL' if field_attr['type'] not in ['text', 'timestamp'] else 'NULL'

        field_default = 'DEFAULT '
        if field_name == 'id':
            field_default = 'AUTO_INCREMENT PRIMARY KEY'
        elif field_attr['type'] == 'string' and field_name != 'id':
            # 非主键的字符串字段的默认值为''
            field_default += '\'\''
        elif field_attr['type'] in ('integer', 'decimal'):
            # 数字字段的默认值为0
            field_default += '0'
        elif field_name == 'create_time':
            field_default += 'CURRENT_TIMESTAMP'
        elif field_name == 'update_time':
            # mysql同一个表中不能有两个字段默认值是当前时间
            field_default += 'NULL ON UPDATE CURRENT_TIMESTAMP'
        else:
            field_default = ''

        field_comment = 'COMMENT \'' + field_attr['comment'] + '\'' if 'comment' in field_attr else ''

        field_dict = {'field_name': field_name, 'field_type': field_type, 'field_size': field_size,
                      'field_notnull': field_notnull, 'field_default': field_default, 'field_comment': field_comment}
        field_list_str += '    ' + template_field.format(**field_dict)
    field_list_str = field_list_str.rstrip('\n,')
    sql = template_table.format(table_name=data['table'], field_list_str=field_list_str, table_comment=data['comment'])
    print(sql)
    with open("../db/sql.txt", "a", encoding='utf-8') as sqlFile:
        sqlFile.write(sql)


if __name__ == '__main__':
    for table in table_list:
        parse(table)
