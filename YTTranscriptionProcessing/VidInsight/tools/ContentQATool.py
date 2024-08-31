from agency_swarm.tools import BaseTool
from pydantic import Field
from openai import OpenAI 
import os 
from pydantic import BaseModel

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

class ContentQATool(BaseTool):
    """Tool to answer the user questions from the video transcription
    """    
    
    question: str = Field(
        ..., description="The question that need to be answered and related to the video."
    )
    
    def _openai_prompt_helper(self, transcriptions, history):
        messages=[]
        
        transcription_text = ' '.join([item['text'] for item in transcriptions])
        system_message = f"You are a highly knowledgeable and polite AI assistant. Your role is to help users by answering their questions accurately and providing helpful information. Always maintaining a friendly and professional tone. Ensure your responses are clear, concise, and easy to understand, regardless of the subject matter. Please identify the answer from the transcription and the previous chat history.\nThe transcription of the video is as follows:\n{transcription_text}"
        messages.append({"role": "system", "content": system_message})
        
        if history:
            messages.extend(history)    
        
        messages.append({"role": "user", "content": self.question})
        
        class QuestionsAnswerModel(BaseModel):
            answer: str
        
        return messages, QuestionsAnswerModel

    def _ask_openai_for_content_qa(self, transcriptions, history):
        messages, QuestionsAnswerModel = self._openai_prompt_helper(transcriptions, history)
        
        openai_client = OpenAI(api_key=OPENAI_API_KEY)

        response = openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            response_format = QuestionsAnswerModel
        )
        
        response_message = response.choices[0].message
        if response_message.parsed:
            return response_message.parsed.answer, True
        else:
            return response_message.refusal, False

    def run(self):
        """
        Answer the user question from the video transcription and history.
        """
        
        history = self._shared_state.get("history", [])
        transcriptions = self._shared_state.get("video_transcription_list")
        
        if not transcriptions:
            raise Exception("Please extract the transcription first. Then again retru this tool.")

        response, success = self._ask_openai_for_content_qa(transcriptions, history)
        
        if not success:
            raise Exception(str(response))

        history.extend([
            {"role": "user", "content": self.question},
            {"role": "assistant", "content": response}
        ])
        self._shared_state.set("history", history)
         
        return response
    
    
if __name__ == "__main__":
    questions = [
        "My name is Abrondon"
        "What is the agency about?",
        "Whats my name",
        "What issues are discussed in video?"
    ]

    tool = ContentQATool()

    for question in questions:
        tool.question = question
        answer = tool.run()
        print(f"Q: {question}\nA: {answer}\n")
