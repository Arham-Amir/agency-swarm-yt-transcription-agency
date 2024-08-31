from agency_swarm.tools import BaseTool
from pydantic import Field
from youtube_transcript_api import YouTubeTranscriptApi

YOUTUBE_VIDEO_PRE_URL = "https://www.youtube.com/watch?v="


class YouTubeVideoTranscriptionTool(BaseTool):
    """
    A tool for extracting English transcriptions from YouTube videos.
    This tool uses the `youtube-transcript-api` to retrieve accurate transcriptions
    from YouTube videos. It handles English-language videos and returns the
    transcription in plain text.
    """

    video_url: str = Field(
        ..., description="The URL of the YouTube video to transcribe."
    )

    def run(self):
        """
        Extracts the transcription of the specified YouTube video.
        """
        
        shared_video_link = self._shared_state.get("video_link")
        shared_transcriptions = self._shared_state.get("video_transcription_list")
        if shared_video_link is not None and shared_transcriptions is not None:
            return {
            "status": "Transcription extracted successfully. You can run further tools for transcription processing."
        }
        
        try:
            # Step 1: Validate the video URL
            if YOUTUBE_VIDEO_PRE_URL not in self.video_url:
                raise ValueError("Invalid video URL. Provide a correct video URL of the video platform.")

            # Extract transcription
            video_id = self.video_url.replace(YOUTUBE_VIDEO_PRE_URL, "")
            transcription = YouTubeTranscriptApi.get_transcript(video_id, languages=['de', 'en'])
            
            self._shared_state.set("video_link", self.video_url)
            self._shared_state.set("video_transcription_list", transcription)
            
            return {
                "status": "Transcription extracted sucessfully"
            }
        except Exception as e:
            print(e)
            return {
                "status": f"Error while extracting transcription: {e}"
            }

def main():
    video_tool = YouTubeVideoTranscriptionTool()
    try:
        video_tool.video_url="https://www.youtube.com/watch?v=NKrAECt9AZo"
        transcription = video_tool.run()
        print(transcription)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
