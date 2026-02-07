import subprocess
import json


score = 0
for _ in range(0, 3):
    _ = subprocess.check_output(["python3", "launcher.pyz", "gr"])
    with open("logs/results.json", encoding="utf-8") as f:
        data = json.loads(f.read())
        d = data['players'][0]['avatar']['score']
        score += d
        
average = score / 3

print("Average:", average)