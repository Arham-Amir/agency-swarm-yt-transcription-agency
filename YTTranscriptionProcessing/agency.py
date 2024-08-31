from fastapi import FastAPI
from agency_swarm import Agency
from YTTranscriptionProcessing.VidInsight import VidInsight
import gradio as gr
import uvicorn

vid_insight = VidInsight()
agency = Agency([vid_insight],
                shared_instructions='./agency_manifesto.md',
                max_prompt_tokens=25000,
                temperature=0.4,
                )

app = FastAPI()

demo = agency.demo_gradio(server_name="0.0.0.0", server_port=8000)

app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
