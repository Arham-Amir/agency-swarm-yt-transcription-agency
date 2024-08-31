from agency_swarm.agents import Agent


class VidInsight(Agent):
    # def clear_shared_state(self):
    #     self._shared_state.set("history", None)
    #     self._shared_state.set("video_transcription_list", None)
    #     self._shared_state.set("video_link", None)
    
    def __init__(self):
        super().__init__(
            name="VidInsight",
            description="VidInsight oversees the entire transcription and content analysis process for YouTube videos.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
        )
        # self.clear_shared_state()
        
    def response_validator(self, message):
        return message
