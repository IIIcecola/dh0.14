"""
基于 ctrl_expressions_list 列表进行分类
"""
import json
import re
from collections import defaultdict

def extract_base_class(param_name):
    """
    从参数名中提取基础类别
    
    基于命名规律：基础名小写，具体名首字母大写
    例如：
    "noseDownL" -> "nose"
    "browDownR" -> "brow"
    "eyeBlinkL" -> "eye"
    "mouthSmile" -> "mouth"
    
    参数:
    param_name: 参数名称（不包含CTRL_expressions_前缀）
    
    返回:
    str: 基础类别名（小写）
    """
    # 提取连续小写字母直到第一个大写字母或数字
    # 例如: browDownL -> brow, eyeBlinkR -> eye, mouth2Smile -> mouth
    match = re.match(r'^([a-z]+)', param_name)
    if match:
        return match.group(1).lower()
    
    # 如果没有小写字母开头，尝试匹配数字开头的情况
    # 例如: 2browRaise -> 2brow（这种情况较少见）
    match = re.match(r'^([a-z0-9]+)', param_name, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    
    # 如果以上都不匹配，返回整个参数名的小写形式
    return param_name.lower()

def group_expression_classes_from_list(ctrl_expressions_list):
    """
    直接从ctrl_expressions_list中提取并分组面部参数类别
    
    参数:
    ctrl_expressions_list: 预定义的面部参数通道列表
    
    返回:
    dict: 基础类别到索引列表的映射字典
    """
    # 使用defaultdict自动初始化列表
    classes_dict = defaultdict(list)
    
    # 遍历ctrl_expressions_list中的所有参数
    for idx, full_param_name in enumerate(ctrl_expressions_list):
        # 确保参数名以"CTRL_expressions_"开头
        if full_param_name.startswith("CTRL_expressions_"):
            # 提取参数名（去掉CTRL_expressions_前缀）
            param_name = full_param_name[len("CTRL_expressions_"):]
            
            # 提取基础类别
            base_class = extract_base_class(param_name)
            
            # 添加当前索引到对应类别的列表
            classes_dict[base_class].append(idx)
        else:
            # 如果不是以"CTRL_expressions_"开头，可能需要特殊处理
            # 这里我们将其视为基础类别为"other"
            print(f"警告: 参数 '{full_param_name}' 不以 'CTRL_expressions_' 开头")
            classes_dict["other"].append(idx)
    
    # 将defaultdict转换为普通字典，并对每个列表排序
    result = {cls: sorted(indices) for cls, indices in classes_dict.items()}
    return result

def generate_classification_json(output_path="expression_classes.json"):
    """
    从ctrl_expressions_list生成分类JSON文件
    
    参数:
    output_path: 输出的JSON文件路径
    """
    try:
        # 导入ctrl_expressions_list
        from PreProcess import ctrl_expressions_list
        
        print(f"成功导入ctrl_expressions_list，包含 {len(ctrl_expressions_list)} 个通道")
        
        # 生成分类
        classification = group_expression_classes_from_list(ctrl_expressions_list)
        
        # 保存到JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(classification, f, indent=2, ensure_ascii=False)
        
        print(f"JSON文件已生成: {output_path}")
        print(f"提取的类别数量: {len(classification)}")
        
        # 统计每个类别的参数数量
        print("\n类别统计:")
        total_params = 0
        sorted_classes = sorted(classification.items(), key=lambda x: (-len(x[1]), x[0]))
        
        for class_name, indices in sorted_classes:
            param_count = len(indices)
            total_params += param_count
            print(f"  {class_name}: {param_count}个参数")
        
        print(f"总参数数量: {total_params}")
        
        # 显示每个类别的前几个参数示例
        print("\n参数分布详情:")
        for class_name, indices in sorted_classes[:10]:  # 显示前10个类别
            print(f"\n{class_name}类 (共{len(indices)}个参数):")
            # 显示前5个索引对应的参数名
            sample_indices = indices[:5]
            for idx in sample_indices:
                if idx < len(ctrl_expressions_list):
                    param_name = ctrl_expressions_list[idx]
                    # 提取基础名部分以便验证
                    if param_name.startswith("CTRL_expressions_"):
                        base_name = param_name[len("CTRL_expressions_"):]
                        base_class = extract_base_class(base_name)
                        print(f"  索引 {idx}: {param_name} -> {base_class}")
                    else:
                        print(f"  索引 {idx}: {param_name}")
            
            if len(indices) > 5:
                print(f"  ... 还有 {len(indices)-5} 个参数")
        
        return classification
        
    except ImportError as e:
        print(f"错误: 无法导入ctrl_expressions_list - {str(e)}")
        print("请确保PreProcess模块在Python路径中")
        return None
    except AttributeError as e:
        print(f"错误: PreProcess模块中没有ctrl_expressions_list - {str(e)}")
        return None
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    主函数
    """
    print("面部参数分类器 - 基于ctrl_expressions_list")
    print("=" * 60)
    
    # 生成分类JSON文件
    result = generate_classification_json("expression_classes.json")
    
    if result:
        print("\n分类完成！")
        print("输出格式示例:")
        print(json.dumps({k: v[:3] for k, v in list(result.items())[:3]}, indent=2))

if __name__ == "__main__":
    main()
