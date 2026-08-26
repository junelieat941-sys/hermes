#!/bin/bash
# 三联视频生成脚本 - 修复版
cd /workspaces/hermes-agent/assets/new\ videos

V="merged-10101010101010010101010.mp4"
BGM="/workspaces/hermes-agent/assets/YTDown.com_YouTube_Runway-Dreams-Chill-Pop-MV-Uplifting-Rom_Media_SOZKhgyEIcY_009_128k.mp3"
DURATION=172.486531
FADE_START=$(echo "$DURATION - 3" | awk '{printf "%.6f", $1-3}')

echo "[1/4] 生成三联视频..."
ffmpeg -hide_banner -loglevel error -y -stream_loop -1 -i "$V" \
  -filter_complex "[0:v]crop=598:1080:0:0,scale=640:1142,crop=640:1080:0:20,setsar=1[base];[base]split=3[part1][part2][part3];[part1][part2][part3]hstack=3[tript]" \
  -map "[tript]" -t $DURATION -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -aspect 16:9 v_test_triptych.mp4

echo "[2/4] 生成标题卡..."
ffmpeg -hide_banner -y -f lavfi -i "color=c=black:s=1920x1080:d=2" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -aspect 16:9 v_test_title.mp4

echo "[3/4] 合并..."
ffmpeg -hide_banner -y -i v_test_title.mp4 -i v_test_triptych.mp4 \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" -map "[v]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -aspect 16:9 v_test_combined.mp4

echo "[4/4] 添加BGM..."
ffmpeg -hide_banner -y -i v_test_combined.mp4 -i "$BGM" \
  -c:v copy -c:a aac -b:a 192k -t $DURATION \
  -af "afade=t=out:st=$FADE_START:d=3" -map 0:v -map 1:a -shortest v_test_final.mp4

echo "完成！"
ls -lh v_test_final.mp4
