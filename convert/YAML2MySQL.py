#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert yml to sql. Support Mysql5.6+
"""
import yaml

table_dict = ['house']
template_table = '''
CREATE TABLE `{table_name}` (
{field_list_str}
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='{table_comment}';
'''
template_field = '`{field_name}` {field_type}{field_size} {field_notnull} {field_comment},\n'
field_type_dict = {
    'integer': 'int',
    'decimal': 'decimal',
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

        field_scale = ',' + str(field_attr['scale']) \
            if field_attr['type'] == 'decimal' and 'scale' in field_attr else ''
        field_size = '(' + str(field_attr['size']) + field_scale + ')' \
            if field_attr['type'] not in ['text', 'timestamp'] and 'size' in field_attr else ''

        field_notnull = 'NOT NULL' if field_attr['type'] not in ['text', 'timestamp'] else 'NULL'

        field_comment = 'COMMENT \'' + field_attr['comment'] + '\'' if 'comment' in field_attr else ''

        field_dict = {'field_name': field_name, 'field_type': field_type, 'field_size': field_size,
                      'field_notnull': field_notnull, 'field_comment': field_comment}
        field_list_str += '    ' + template_field.format(**field_dict)

    field_list_str = field_list_str[0:-2]  # remove the last \n and ,
    sql = template_table.format(table_name=data['table'], field_list_str=field_list_str, table_comment=data['comment'])
    print(sql)
    with open("../db/sql.txt", "w", encoding='utf-8') as sqlFile:
        sqlFile.write(sql)


if __name__ == '__main__':
    for table in table_dict:
        parse(table)
