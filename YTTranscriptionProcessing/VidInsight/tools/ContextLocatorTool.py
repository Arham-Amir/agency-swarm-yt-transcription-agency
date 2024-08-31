from agency_swarm.tools import BaseTool
from pydantic import Field
from openai import OpenAI 
import os 
from pydantic import BaseModel

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

class ContextLocatorTool(BaseTool):
    """
    Pinpoints specific contexts or concepts discussed in the video with exact timestamps.
    Analyzes the transcription using OpenAI to identify key topics and their corresponding timestamps.

    This tool should only be executed when the user prompt contains a "where" or "when" type of clause.
    If the prompt is a question or unrelated to investigating specific topics, do not run this tool.
    """

    topic: str = Field(
        ..., description="The specific context or concept to locate in the video."
    )
    
    def _openai_prompt_helper(self, transcription):
        system_message = (
            "You are an AI assistant that helps identify where specific topics are discussed in a YouTube video."
            "You are provided with the transcription of the video content, including timestamps, and a specific topic."
            "Your task is to locate the exact timestamps where the topic is discussed and provide them with a clear context line of max 6-12 words."
            "The timestamps must be properly converted into minutes and hours, as they are shown in the video."
        )
        transcription_text = "\n".join(
            [f"{entry['start']}: {entry['text']}" for entry in transcription]
        )
        user_message = (
            f"The topic to locate is: '{self.topic}'. Please identify the timestamps where this topic is discussed.\n\n"
            f"The transcription of the video is as follows:\n\n{transcription_text}"
        )
        
        class ContextLocatorResponse(BaseModel):
            class Context(BaseModel):
                sentence_initials: str
                timestamp: str
                    
            context_timestamps: list[Context]
            
        return system_message, user_message, ContextLocatorResponse
  
    def _ask_openai_for_context_locator(self, transcription):
        system_message, user_message, ContextLocatorResponse = self._openai_prompt_helper(transcription)
        
        openai_client = OpenAI(api_key=OPENAI_API_KEY)

        response = openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            response_format = ContextLocatorResponse
        )
        
        response_message = response.choices[0].message
        if response_message.parsed:
            return response_message.parsed.context_timestamps
        elif response_message.refusal:
            return response_message.refusal

    def run(self):
        """
        Identifies the timestamps where the specified topic is discussed in the video transcription.
        """
        transcription = self._shared_state.get("video_transcription_list")
        
        if not transcription:
            raise Exception("Please extract the transcription first. Then again return to this tool.")
        
        response = self._ask_openai_for_context_locator(transcription)
        
        if not isinstance(response, list):
            raise Exception(str(response))
        
        response_obj = {
           col.timestamp: col.sentence_initials for col in response
        }
        
        return response_obj
        

def main():
    tool = ContextLocatorTool()
    tool.topic= "code analysis"

    result = tool.run()
    print(result)

if __name__ == "__main__":
    main()