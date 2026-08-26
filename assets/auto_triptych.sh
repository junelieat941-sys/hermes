#!/bin/bash
# 全自动三联视频生成器 v2
# 用法: bash auto_triptych.sh <视频文件> [标题]

cd /workspaces/hermes-agent/assets/new\ videos

V="${1:?请提供视频文件路径}"
TITLE="${2:-作品}"
BGM="/workspaces/hermes-agent/assets/YTDown.com_YouTube_Runway-Dreams-Chill-Pop-MV-Uplifting-Rom_Media_SOZKhgyEIcY_009_128k.mp3"
DURATION=172.486531
FADE_START=$(echo "$DURATION - 3" | awk '{printf "%.6f", $1-3}')

# 提取视频名称
VIDEO_NAME=$(basename "$V" .mp4)
OUTPUT_NAME="${VIDEO_NAME}_final"

echo "============================================================"
echo "全自动三联视频生成器"
echo "============================================================"
echo "视频: $V"
echo "标题: $TITLE"
echo ""

# [1/4] 生成三联视频
echo "[1/4] 生成三联视频..."
ffmpeg -hide_banner -loglevel error -y -stream_loop -1 -i "$V" \
  -filter_complex "[0:v]crop=598:1080:0:0,scale=640:1142,crop=640:1080:0:20,setsar=1[base];[base]split=3[part1][part2][part3];[part1][part2][part3]hstack=3[tript]" \
  -map "[tript]" -t $DURATION -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -aspect 16:9 "${OUTPUT_NAME}_triptych.mp4"

if [ ! -f "${OUTPUT_NAME}_triptych.mp4" ]; then
    echo "✗ 三联视频生成失败"
    exit 1
fi
echo "✓ 三联视频完成"

# [2/4] 生成标题卡
echo "[2/4] 生成标题卡..."
ffmpeg -hide_banner -y -f lavfi -i "color=c=black:s=1920x1080:d=2" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -aspect 16:9 "${OUTPUT_NAME}_title.mp4"
echo "✓ 标题卡完成"

# [3/4] 合并
echo "[3/4] 合并视频..."
ffmpeg -hide_banner -y -i "${OUTPUT_NAME}_title.mp4" -i "${OUTPUT_NAME}_triptych.mp4" \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" -map "[v]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -aspect 16:9 "${OUTPUT_NAME}_combined.mp4"
echo "✓ 合并完成"

# [4/4] 添加BGM
echo "[4/4] 添加BGM..."
ffmpeg -hide_banner -y -i "${OUTPUT_NAME}_combined.mp4" -i "$BGM" \
  -c:v copy -c:a aac -b:a 192k -t $DURATION \
  -af "afade=t=out:st=$FADE_START:d=3" -map 0:v -map 1:a -shortest "${OUTPUT_NAME}.mp4"

if [ ! -f "${OUTPUT_NAME}.mp4" ]; then
    echo "✗ 添加BGM失败"
    exit 1
fi
echo "✓ BGM添加完成"

# 生成封面
echo "生成封面..."
ffmpeg -hide_banner -y -ss 0.1 -i "$V" -frames:v 1 -update 1 /tmp/hero_frame.jpg
ffmpeg -hide_banner -y -i /tmp/hero_frame.jpg -vf "scale=1280:720:flags=lanczos,drawtext=text='$TITLE':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" "${OUTPUT_NAME}_cover.png"
rm -f /tmp/hero_frame.jpg
echo "✓ 封面完成"

# 上传到gofile.io
echo ""
echo "============================================================"
echo "上传到 gofile.io..."
echo "============================================================"
SERVER=$(curl -s --max-time 20 https://api.gofile.io/servers | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['servers'][0]['name'])")
curl -s --max-time 600 -F "file=@${OUTPUT_NAME}.mp4" "https://${SERVER}.gofile.io/contents/uploadfile" -o /tmp/up_final.json
URL=$(python3 -c "import json; d=json.load(open('/tmp/up_final.json')); print(d['data']['downloadPage'])")

echo ""
echo "============================================================"
echo "✓ 完成！"
echo "============================================================"
echo "视频: ${OUTPUT_NAME}.mp4"
echo "封面: ${OUTPUT_NAME}_cover.png"
echo "下载: $URL"
echo "============================================================"
