from agency_swarm.tools import BaseTool
from pydantic import Field
from openai import OpenAI 
import os 
from pydantic import BaseModel

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

class SummarisedPostTool(BaseTool):
    """
    Tool for summarizing YouTube video transcriptions into engaging social media post content.
    """
    
    def _openai_prompt_helper(self, transcriptions, video_link):
        messages=[{"role": "system", "content": "You are a skilled social media content creator."}]
        transcription_text = ' '.join([item['text'] for item in transcriptions])
        
        system_message = "You are a skilled social media content creator. Below is a transcription of a YouTube video. Summarize the key points of the transcription and create a detailed, engaging, and attractive social media post. The post should emphasize the main ideas and tips shared in the video, making it informative and appealing. Include key takeaways, and at the end, add a call-to-action phrase such as 'For more details, check out this video!' to encourage viewers to watch the full video."
        
        messages.extend([
            {"role": "user", "content": system_message},
            {"role": "user", "content": f"This is a youtube video link: {video_link}"}, 
            {"role": "user", "content": transcription_text}
        ])
        
        class PostContentGeneratorModel(BaseModel):
            post_content: str
        
        return messages, PostContentGeneratorModel

    def _ask_openai_for_post_content(self, transcriptions, video_link):
        messages, PostContentGeneratorModel = self._openai_prompt_helper(transcriptions, video_link)
        
        openai_client = OpenAI(api_key=OPENAI_API_KEY)

        response = openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            response_format = PostContentGeneratorModel
        )
        
        response_message = response.choices[0].message
        if response_message.parsed:
            return response_message.parsed.post_content, True
        else:
            return response_message.refusal, False

    def run(self):
        """
        Summarised the youtube video transcript to create a explanatory social media post
        """
        video_link = self._shared_state.get("video_link")
        transcriptions = self._shared_state.get("video_transcription_list")
        
        if not transcriptions:
            raise Exception("Please extract the transcription first. Then again return to this tool.")

        response, success = self._ask_openai_for_post_content(transcriptions, video_link)
        
        if not success:
            raise Exception(str(response))
         
        return response
    
    
if __name__ == "__main__":
    tool = SummarisedPostTool()
    answer = tool.run()
    print(answer)
