#!/bin/bash

# 音频视频处理批量脚本
# 用法: ./batch_process.sh [--overwrite]

PYTHON_SCRIPT="./wav2video.py"
SERVER_URL="http://127.0.0.1:8084/send_json"

# 解析参数
OVERWRITE=""
if [[ "$1" == "--overwrite" ]]; then
    OVERWRITE="--overwrite"
    echo "启用覆盖模式"
fi

# 定义批处理任务列表
# 格式: "json_path|wave_path|video_path|default_wave_path"
# 注意: default_wave_path是可选的
tasks=(
    "/path/to/json_files_1|/path/to/audio_files_1|/path/to/output_videos_1|/path/to/default.wav"
    "/path/to/json_files_2|/path/to/audio_files_2|/path/to/output_videos_2|"
    "/path/to/json_files_3|/path/to/audio_files_3|/path/to/output_videos_3|/path/to/fallback.wav"
)

echo "开始批量处理任务..."
echo "总任务数: ${#tasks[@]}"
echo "========================================"

# 处理每个任务
for i in "${!tasks[@]}"; do
    task="${tasks[$i]}"
    
    # 解析任务参数
    IFS='|' read -r json_path wave_path video_path default_wave_path <<< "$task"
    
    echo ""
    echo "处理任务 $((i+1))/${#tasks[@]}:"
    echo "  JSON路径: $json_path"
    echo "  音频路径: $wave_path"
    echo "  输出路径: $video_path"
    
    # 检查必要目录是否存在
    if [[ ! -d "$json_path" ]]; then
        echo "  ❌ JSON目录不存在，跳过此任务"
        continue
    fi
    
    if [[ ! -d "$wave_path" ]]; then
        echo "  ⚠️  音频目录不存在，尝试使用默认音频"
    fi
    
    # 构建Python命令
    PYTHON_CMD="python3 \"$PYTHON_SCRIPT\" \
        --json-path \"$json_path\" \
        --wave-path \"$wave_path\" \
        --save-video-path \"$video_path\" \
        --server-url \"$SERVER_URL\" \
        --fps 25"
    
    # 添加可选参数
    if [[ -n "$default_wave_path" && -f "$default_wave_path" ]]; then
        PYTHON_CMD="$PYTHON_CMD --default-wave-path \"$default_wave_path\""
        echo "  使用默认音频: $default_wave_path"
    fi
    
    if [[ -n "$OVERWRITE" ]]; then
        PYTHON_CMD="$PYTHON_CMD $OVERWRITE"
    fi
    
    # 创建输出目录
    mkdir -p "$video_path"
    
    echo "  执行命令..."
    echo "========================================"
    
    # 执行命令
    start_time=$(date +%s)
    eval $PYTHON_CMD
    exit_code=$?
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✅ 任务完成 (耗时: ${duration}秒)"
    else
        echo "  ❌ 任务失败 (耗时: ${duration}秒)"
    fi
    echo "========================================"
done

echo ""
echo "所有任务处理完成！"
