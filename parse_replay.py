# GitHub: https://github.com/Liovovo/pubg-bridge-replay-analyzer

import json
import base64
import gzip
import sys


def parse_replaydata(input_file: str, output_file: str = None) -> dict:
    """
    replayData是经过gzip压缩后再进行base64编码的数据
    解码流程: base64解码 -> gzip解压缩 -> JSON
    
    Args:
        input_file: replaydata.json文件路径
        output_file: 可选，输出解析后的JSON文件路径
    
    Returns:
        解析后的Python字典
    """
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取base64编码的压缩数据
    replay_data_b64 = data.get('replayData', '')
    
    if not replay_data_b64:
        raise ValueError("输入文件中未找到replayData字段或该字段为空")
    
    # 1. Base64解码 -> 得到gzip压缩的二进制数据
    compressed_data = base64.b64decode(replay_data_b64)
    
    # 2. gzip解压缩 -> 得到原始JSON字符串
    decompressed_data = gzip.decompress(compressed_data)
    
    # 3. 解析JSON字符串为Python对象
    parsed_data = json.loads(decompressed_data.decode('utf-8'))
    
    # 如果指定了输出文件，则保存
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        print(f"解析后的数据已保存到: {output_file}")
    
    return parsed_data


def generate_output_filename(parsed_data: dict) -> str:
    m = parsed_data.get('m', {})
    t = parsed_data.get('t', {})
    
    parts = ['replay']
    
    # 地图名称 (m.n 或 t.m)
    map_name = m.get('n') or t.get('m')
    if map_name:
        parts.append(map_name)
    
    # 天气
    weather = m.get('w')
    if weather:
        parts.append(weather)
    
    # 比赛时长
    match_length = m.get('l')
    if match_length:
        parts.append(f"{match_length}s")
    
    return f"{'_'.join(parts)}.json"


def main():
    if len(sys.argv) < 2:
        print("用法: python parse_replay.py <文件名>")
        print("示例: python parse_replay.py replaydata.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        result = parse_replaydata(input_file)
        output_file = generate_output_filename(result)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"解析后的数据已保存到: {output_file}")
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_file}'")
    except Exception as e:
        print(f"解析失败: {e}")


if __name__ == '__main__':
    main()
