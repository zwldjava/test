import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Union


class DataReader:
    def __init__(self, data_dir: Union[str, Path] = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent / "tests" / "data"
        else:
            self.data_dir = Path(data_dir)
        
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)

    def read_yaml(self, file_name: str) -> Union[Dict, List]:
        file_path = self.data_dir / f"{file_name}.yaml"
        
        if not file_path.exists():
            file_path = self.data_dir / f"{file_name}.yml"
        
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def read_json(self, file_name: str) -> Union[Dict, List]:
        file_path = self.data_dir / f"{file_name}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def read(self, file_name: str) -> Union[Dict, List]:
        yaml_path = self.data_dir / f"{file_name}.yaml"
        yml_path = self.data_dir / f"{file_name}.yml"
        json_path = self.data_dir / f"{file_name}.json"
        
        if yaml_path.exists():
            return self.read_yaml(file_name)
        elif yml_path.exists():
            return self.read_yaml(file_name)
        elif json_path.exists():
            return self.read_json(file_name)
        else:
            raise FileNotFoundError(f"数据文件不存在: {file_name}")

    def get_test_cases(self, file_name: str) -> List[Dict]:
        data = self.read(file_name)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "test_cases" in data:
            return data["test_cases"]
        elif isinstance(data, dict):
            return [data]
        else:
            raise ValueError(f"无法解析测试数据: {file_name}")

    def get_test_data(self, file_name: str, key: str = None) -> Any:
        data = self.read(file_name)
        
        if key is None:
            return data
        elif isinstance(data, dict):
            return data.get(key)
        else:
            raise ValueError(f"数据不是字典类型，无法获取键: {key}")

    def list_data_files(self) -> List[str]:
        files = []
        for ext in ["*.yaml", "*.yml", "*.json"]:
            files.extend(self.data_dir.glob(ext))
        return [f.stem for f in files]
