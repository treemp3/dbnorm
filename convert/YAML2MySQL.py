#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert yml to sql. Support Mysql5.6+
"""
import yaml

table_list = ['装备表', '项目表', '摄像头表', '维保计划', '工单表', '工厂表', '供应商分类', '供应商档案',
              '标准工序', '工艺路线', '工艺路线明细', '产出物料', '物流档案', '产线档案', '设备档案', '车间工段工位',
              '质检项', '质检方案', '质检项列表', '设计BOM', '设计BOM明细', '销售客户', '销售线索', '销售跟进', '销售转移记录',
              '生产订单', '生产订单明细', '设计图纸', '出厂资料', '生产BOM', '作业计划', '员工报工时', '报工单',
              '过程检验单', '过程检验单明细', '不合格品', '请购单', '请购单明细', '采购订单', '采购订单明细', '采购到货记录',
              '公司信息', '常见问题', '投诉建议', '装备配件', '产品预订',
              '配送计划', '配送计划明细', '领料配送单', '领料配送单明细', '配送收料记录',
              '仓库管理', '单据类型', '收发记录', '收发记录明细']
template_table = '''
CREATE TABLE `{table_name}` (
{field_list_str}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{table_comment}';
'''
template_field = '`{field_name}` {field_type}{field_size} {field_notnull} {field_default} {field_comment},\n'
field_type_dict = {
    'integer': 'int',
    'decimal': 'decimal',
    'string': 'varchar',
    'text': 'text',
    'timestamp': 'timestamp',
    'datetime': 'datetime',
    'date': 'date',
    'time': 'time'
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
            if field_attr['type'] not in ['text', 'timestamp', 'datetime', 'date', 'time'] and 'size' in field_attr \
            else ''

        field_notnull = 'NOT NULL' \
            if field_attr['type'] not in ['text', 'timestamp', 'datetime', 'date', 'time'] else 'NULL'

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
