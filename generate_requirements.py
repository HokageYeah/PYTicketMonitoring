import subprocess
import sys

def generate_requirements():
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(result.stdout)
        
        print("requirements.txt 文件已成功生成！")
    except Exception as e:
        print(f"生成 requirements.txt 时出错: {e}")

if __name__ == "__main__":
    generate_requirements()