import subprocess

successful_runs = 0
total = 0
for _ in range(0, 50):
    success = bool("0xSUCCESSx0" in subprocess.check_output(["python3", "launcher.pyz", "gr"]).decode())
    total += 1
    if success:
        successful_runs += 1
    
average = successful_runs / total
print("Successful Runs:", successful_runs)
print("Total:", total)
print(f"Average Bot Evade: {average*100}%", )