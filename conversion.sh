download_url=$1
#echo -e "\n\n\n\n$download_url\n\n\n\n"
video_name=$2
video_file=$(basename "$video_name")


job_480p=$(curl -s -X POST "https://api.cloudconvert.com/v2/jobs" -H "Authorization: Bearer $CLOUDCONVERT_API_KEY" -H "Content-type: application/json" -d '{"tasks":{"import":{"operation":"import/url","url":"'"$download_url"'"},"480p":{"operation":"convert","input_format":"mp4","output_format":"mp4","engine":"ffmpeg","input":["import"],"video_codec":"x264","crf":23,"preset":"medium","width":640,"height":480,"fit":"scale","aspect_ratio":"16:9","subtitles_mode":"none","audio_codec":"aac","audio_bitrate":128},"export":{"operation":"export/url","input":["480p"],"inline":false,"archive_multiple_files":false}},"tag":"jobbuilder-480p"}')
job_id_480p=$(echo $job_480p | jq -r '.data.id')

job_720p=$(curl -s -X POST "https://api.cloudconvert.com/v2/jobs" -H "Authorization: Bearer $CLOUDCONVERT_API_KEY" -H "Content-type: application/json" -d '{"tasks":{"import":{"operation":"import/url","url":"'"$download_url"'"},"720p":{"operation":"convert","input_format":"mp4","output_format":"mp4","engine":"ffmpeg","input":["import"],"video_codec":"x264","crf":23,"preset":"medium","width":1280,"height":720,"fit":"scale","aspect_ratio":"16:9","subtitles_mode":"none","audio_codec":"aac","audio_bitrate":128},"export":{"operation":"export/url","input":["720p"],"inline":false,"archive_multiple_files":false}},"tag":"jobbuilder-720p"}')
job_id_720p=$(echo $job_720p | jq -r '.data.id')

echo "Waiting for 480p job to finish..."
job_status=$(curl -s -g "https://sync.api.cloudconvert.com/v2/jobs/$job_id_480p" -H "Authorization: Bearer $CLOUDCONVERT_API_KEY")
echo "480p job done."
download_url_480p=$(echo $job_status | jq -r '.data.tasks[0].result.files[0].url')
curl -L -o "${video_name}_480p.mp4" $download_url_480p

echo "Waiting for 720p job to finish..."
job_status=$(curl -s -g "https://sync.api.cloudconvert.com/v2/jobs/$job_id_720p" -H "Authorization: Bearer $CLOUDCONVERT_API_KEY")
echo "720p job done."
download_url_720p=$(echo $job_status | jq -r '.data.tasks[0].result.files[0].url')
curl -L -o "${video_name}_720p.mp4" $download_url_720p
