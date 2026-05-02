# PUBG BRIDGE Replay Analyzer

本仓库用于存储与存档PUBG遥测文件及Bridge回放分析相关内容。

![预览](demo/img.jpg)

## PUBG Bridge

### 解析回放数据

```bash
python parse_replay.py replaydata.json
```

### 可视化查看

打开 `visualizer.html`，把PUBG Bridge的原始或解析后的 JSON 拖进去即可。

### 数据来源

```
https://bridge.pubg.com/api/v1/web-replay/replays/{replay_match_id}
```

支持的功能：

- 事件可视化
- 简易2D回放

## PUBG API

### 遥测数据

`/data`：部分数据  
`/telemetry`：遥测相关备份存档

## 声明

PUBG BRIDEG的回放数据与PUBGAPI的telemetry无关。  
本项目与 Krafton 及其关联公司无关，相关图片、图标和商标均属于其各自所有者。  
本项目仅供学习和研究，不得用于非法用途。

## License

MIT
