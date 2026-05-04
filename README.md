# PUBG BRIDGE Replay Analyzer

This repository is for personal storage and archiving of PUBG maps, telemetry, and Bridge replay related content.

![Preview](demo/img.jpg)

## PUBG Bridge

### Parse Replay Data

```bash
python parse_replay.py replaydata.json
```

### Visualize

Open `visualizer.html` and drag the raw or parsed JSON from PUBG Bridge into it.

### Data Source

```
https://bridge.pubg.com/api/v1/web-replay/replays/{replay_match_id}
```

Supported Features:

- Event visualization
- Simple 2D replay

## PUBG API

### Telemetry

`/data/Points`: Point data  
`/telemetry`: Telemetry related backup archives

## Maps

### HeightMap

`/data/HeightMap`: HeightMap exports

## Disclaimer

PUBG BRIDGE replay data is unrelated to PUBG API telemetry.  
This project is not affiliated with Krafton or its associated companies. Related images, icons, and trademarks belong to their respective owners.  
This project is for educational and research purposes only and must not be used for illegal purposes.

## License

MIT
