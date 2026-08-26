#!/usr/bin/env python3
"""
全自动三联视频生成器 v2
用法: python3 auto_triptych.py <视频文件路径> [标题]
"""
import os
import sys
import subprocess
import json
import argparse
from pathlib import Path

# 配置
BGM_PATH = "/workspaces/hermes-agent/assets/YTDown.com_YouTube_Runway-Dreams-Chill-Pop-MV-Uplifting-Rom_Media_SOZKhgyEIcY_009_128k.mp3"
BGM_DURATION = 172.486531
FADE_START = BGM_DURATION - 3

def run_cmd(cmd, desc=""):
    """运行命令并返回结果"""
    print(f"  {desc}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ 错误: {result.stderr[-200:] if result.stderr else 'Unknown'}")
        return False
    return True

def get_video_info(video_path):
    """获取视频信息"""
    cmd = f'ffprobe -v quiet -print_format json -show_format -show_streams "{video_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
        video_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
        if not video_stream:
            return None
        format_info = data['format']
        fps = eval(video_stream['avg_frame_rate'])
        return {
            'width': int(video_stream['width']),
            'height': int(video_stream['height']),
            'duration': float(format_info['duration']),
            'fps': fps,
            'codec': video_stream['codec_name']
        }
    except Exception as e:
        print(f"  ✗ 解析失败: {e}")
        return None

def generate_triptych(video_path, output_path):
    """生成三联视频"""
    info = get_video_info(video_path)
    if not info:
        print("  ✗ 无法获取视频信息")
        return False
    
    w, h = info['width'], info['height']
    aspect = w / h
    print(f"  分辨率: {w}x{h}, 宽高比: {aspect:.2f}")
    
    # 简化处理：固定裁剪比例
    # 横屏视频裁竖内容
    if aspect > 1.3:
        crop_w, crop_h, crop_x, crop_y = 598, 1080, 0, 0
    else:
        crop_w, crop_h, crop_x, crop_y = w, h, 0, 0
    
    # 等比缩放到640宽
    scale_h = int(640 * crop_h / crop_w)
    
    if scale_h > 1080:
        # 需要裁上下
        offset_y = (scale_h - 1080) // 2
        filter_complex = f"[0:v]crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale=640:{scale_h},crop=640:1080:0:{offset_y},setsar=1[base];[base]split=3[part1][part2][part3];[part1][part2][part3]hstack=3[tript]"
    else:
        # 需要填上下
        offset_y = (1080 - scale_h) // 2
        filter_complex = f"[0:v]crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale=640:{scale_h},pad=640:1080:0:{offset_y},setsar=1[base];[base]split=3[part1][part2][part3];[part1][part2][part3]hstack=3[tript]"
    
    cmd = f'ffmpeg -hide_banner -loglevel error -y -stream_loop -1 -i "{video_path}"'
    cmd += f' -filter_complex "{filter_complex}"'
    cmd += f' -map "[tript]" -t {BGM_DURATION}'
    cmd += f' -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -aspect 16:9 "{output_path}"'
    
    print(f"  生成三联视频 (预计~15分钟)...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0 and os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"  ✓ 三联视频完成 ({size_mb:.0f}MB)")
        return True
    else:
        print(f"  ✗ 生成失败")
        if result.stderr:
            print(f"  错误: {result.stderr[-300:]}")
        return False

def generate_title_card(output_path):
    """生成2秒标题卡"""
    print(f"  生成标题卡...")
    cmd = f'ffmpeg -hide_banner -y -f lavfi -i "color=c=black:s=1920x1080:d=2" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -aspect 16:9 "{output_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓ 标题卡完成")
        return True
    print(f"  ✗ 标题卡生成失败")
    return False

def concat_videos(title_path, triptych_path, output_path):
    """合并视频"""
    print(f"  合并视频...")
    cmd = f'ffmpeg -hide_banner -y -i "{title_path}" -i "{triptych_path}"'
    cmd += f' -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" -map "[v]"'
    cmd += f' -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -aspect 16:9 "{output_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(output_path):
        print(f"  ✓ 合并完成")
        return True
    print(f"  ✗ 合并失败: {result.stderr[-200:]}")
    return False

def add_bgm(combined_path, output_path):
    """添加BGM"""
    print(f"  添加BGM...")
    cmd = f'ffmpeg -hide_banner -y -i "{combined_path}" -i "{BGM_PATH}"'
    cmd += f' -c:v copy -c:a aac -b:a 192k -t {BGM_DURATION}'
    cmd += f' -af "afade=t=out:st={FADE_START}:d=3"'
    cmd += f' -map 0:v -map 1:a -shortest "{output_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(output_path):
        print(f"  ✓ BGM添加完成")
        return True
    print(f"  ✗ BGM添加失败: {result.stderr[-200:]}")
    return False

def generate_cover(video_path, cover_path, title="作品"):
    """生成封面"""
    print(f"  生成封面...")
    hero_path = "/tmp/hero_frame.jpg"
    
    # 提取第一帧
    cmd = f'ffmpeg -hide_banner -y -ss 0.1 -i "{video_path}" -frames:v 1 -update 1 "{hero_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0 or not os.path.exists(hero_path):
        print(f"  ✗ 无法提取帧")
        return False
    
    # 生成封面
    cmd = f'ffmpeg -hide_banner -y -i "{hero_path}"'
    cmd += f' -vf "scale=1280:720:flags=lanczos,drawtext=text=\'{title}\':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2"'
    cmd += f' "{cover_path}"'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    os.remove(hero_path)
    
    if result.returncode == 0 and os.path.exists(cover_path):
        print(f"  ✓ 封面完成")
        return True
    print(f"  ✗ 封面生成失败")
    return False

def upload_to_gofile(file_path):
    """上传到gofile.io"""
    print(f"  上传到 gofile.io...")
    
    # 获取服务器
    result = subprocess.run('curl -s https://api.gofile.io/servers', shell=True, capture_output=True, text=True)
    try:
        servers = json.loads(result.stdout).get('data', {}).get('servers', [])
        server = servers[0]['name'] if servers else 'store-eu-par-4'
    except:
        server = 'store-eu-par-4'
    
    # 上传
    cmd = f'curl -s --max-time 600 -F "file=@{file_path}" "https://{server}.gofile.io/contents/uploadfile"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    try:
        data = json.loads(result.stdout)
        url = data.get('data', {}).get('downloadPage', '')
        if url:
            print(f"  ✓ 上传完成: {url}")
            return url
    except:
        pass
    
    print(f"  ✗ 上传失败")
    return None

def main():
    parser = argparse.ArgumentParser(description='全自动三联视频生成器')
    parser.add_argument('video', help='视频文件路径')
    parser.add_argument('--title', default=None, help='标题名')
    
    args = parser.parse_args()
    
    video_path = args.video
    if not os.path.isabs(video_path):
        # 尝试相对路径
        candidates = [
            video_path,
            f"new videos/{video_path}",
            f"/workspaces/hermes-agent/assets/{video_path}"
        ]
        for cand in candidates:
            if os.path.exists(cand):
                video_path = cand
                break
    
    if not os.path.exists(video_path):
        print(f"✗ 文件不存在: {video_path}")
        sys.exit(1)
    
    print("="*60)
    print("全自动三联视频生成器 v2")
    print("="*60)
    print(f"视频: {video_path}")
    
    # 获取输出目录
    output_dir = os.path.dirname(os.path.abspath(video_path))
    
    # 生成输出文件名
    video_name = Path(video_path).stem
    title = args.title or video_name
    output_name = f"{video_name}_final"
    
    triptych_path = os.path.join(output_dir, f"{output_name}_triptych.mp4")
    combined_path = os.path.join(output_dir, f"{output_name}_combined.mp4")
    final_path = os.path.join(output_dir, f"{output_name}.mp4")
    cover_path = os.path.join(output_dir, f"cover_{video_name}.png")
    title_path = os.path.join(output_dir, f"{output_name}_title.mp4")
    
    # 生成三联视频
    print("\n[1/4] 生成三联视频...")
    if not generate_triptych(video_path, triptych_path):
        sys.exit(1)
    
    # 生成标题卡
    print("\n[2/4] 生成标题卡...")
    if not generate_title_card(title_path):
        sys.exit(1)
    
    # 合并
    print("\n[3/4] 合并视频...")
    if not concat_videos(title_path, triptych_path, combined_path):
        sys.exit(1)
    
    # 添加BGM
    print("\n[4/4] 添加BGM...")
    if not add_bgm(combined_path, final_path):
        sys.exit(1)
    
    # 生成封面
    print("\n生成封面...")
    if not generate_cover(video_path, cover_path, title):
        print("  ⚠ 封面生成失败，继续...")
    
    # 上传
    print("\n" + "="*60)
    print("上传到 gofile.io...")
    print("="*60)
    url = upload_to_gofile(final_path)
    
    print("\n" + "="*60)
    print("✓ 完成！")
    print("="*60)
    print(f"视频: {final_path}")
    print(f"封面: {cover_path}")
    if url:
        print(f"下载: {url}")
    print("="*60)

if __name__ == "__main__":
    main()
