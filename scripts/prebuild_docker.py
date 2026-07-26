import pandas as pd, subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed

def build_image(task_dir):
    dockerfile = f'{task_dir}/environment/Dockerfile'
    if not os.path.exists(dockerfile):
        return task_dir, 'no_dockerfile'
    tag = f'skyrl-prebuild-{os.path.basename(task_dir)}'
    r = subprocess.run(['docker', 'image', 'inspect', tag], capture_output=True)
    if r.returncode == 0:
        return task_dir, 'skipped'
    r = subprocess.run(
        ['docker', 'build', '-t', tag, '-f', dockerfile, f'{task_dir}/environment', '--quiet'],
        capture_output=True, text=True, timeout=300
    )
    return task_dir, 'built' if r.returncode == 0 else f'failed: {r.stderr[-200:]}'

print("Loading parquet...")
train = pd.read_parquet('/home/ec2-user/xin/data_qwen3b/train.parquet')
val = pd.read_parquet('/home/ec2-user/xin/data_qwen3b/validation.parquet')
task_dirs = list(set(
    list(train['extra_info'].apply(lambda x: x['task_dir'])) +
    list(val['extra_info'].apply(lambda x: x['task_dir']))
))
print(f"Pre-building {len(task_dirs)} Docker images with 8 parallel workers...")

counts = {'built': 0, 'skipped': 0, 'failed': 0, 'no_dockerfile': 0}
done = 0
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(build_image, td): td for td in task_dirs}
    for future in as_completed(futures):
        task_dir, status = future.result()
        done += 1
        key = status.split(':')[0]
        counts[key] = counts.get(key, 0) + 1
        if status == 'built' or status.startswith('failed'):
            print(f"[{done}/{len(task_dirs)}] {status}: {os.path.basename(task_dir)}")

print(f"\nDone. {counts}")
