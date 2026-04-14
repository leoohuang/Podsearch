import yaml
from src.ingest import ingest

# 读取 YAML 配置
with open("podcasts.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 批量下载
for pod in config["podcasts"]:
    name = pod["name"]
    count = pod["episodes_to_fetch"]
    print(f"\n===== Downloadig:{name} =====")
    try:
        ingest(name=name, n=count)
    except Exception as e:
        print(f"Failed:{e}")