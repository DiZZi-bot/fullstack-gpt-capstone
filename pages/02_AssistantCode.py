import streamlit as st

body = '''
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
import streamlit as st

st.set_page_config(
    page_title="AssistantGPT",
    page_icon="🕵️"
)

class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event):
        if event.event == "thread.run.requires_action":
            run_id = event.data.id
            self.message = ""
            self.message_box = st.empty()
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_result_ddg":
                tool_outputs.append({"tool_call_id": tool.id, "output": "ddg"})
            elif tool.function.name == "get_result_wiki":
                tool_outputs.append({"tool_call_id": tool.id, "output": "wiki"})

        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            for text in stream.text_deltas:
                self.message += text
                self.message_box.markdown(self.message)
                print(text, end="", flush=True)
        st.session_state["recent_answer"] = self.message

if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = None

if "messages" not in st.session_state:
    st.session_state["messages"] = []

with st.sidebar:
    st.link_button("Github Repo", "https://github.com/DiZZi-bot/fullstack-gpt")
    if not st.session_state["OPENAI_API_KEY"]:
        OPENAI_API_KEY = st.text_input("Input your OpenAI api key", type="password")
        if OPENAI_API_KEY:
            st.session_state["OPENAI_API_KEY"] = OPENAI_API_KEY
            st.success("Get Api Key.")


if not st.session_state["OPENAI_API_KEY"]:
    st.markdown(
        """
        # AssistantGPT
                
        Ask me anything you're curious about.
                
        I find it in duckduckgo and wikipedia.
    """
    )
else:
    if "client" in st.session_state:
        client = st.session_state["client"]
        assistant = st.session_state["assistant"]
        thread = st.session_state["thread"]
    else:
        client = OpenAI(api_key=st.session_state["OPENAI_API_KEY"])
        assistant = client.beta.assistants.create(
            name="Research Assistant",
            instructions="You help research with two tools:DuckDuckGo and Wikipedia. Return the result with tool name on the top.",
            model="gpt-4o-mini",
            temperature=0.1,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_result_ddg",
                        "description": "Get the research result for the query on the DuckDuckGo.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "full string of user's input",
                                },
                            },
                            "required": ["query"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_result_wiki",
                        "description": "Get the research result for the query on the Wikipedia.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "full string of user's input",
                                },
                            },
                            "required": ["query"],
                        },
                    },
                },
            ],
        )
        thread = client.beta.threads.create()
        st.session_state["client"] = client
        st.session_state["assistant"] = assistant
        st.session_state["thread"] = thread

    messages = client.beta.threads.messages.list(thread_id=thread.id)

    if messages:
        messages = list(messages)
        messages.reverse()
        for message in messages:
            st.chat_message(message.role).write(message.content[0].text.value)

    question = st.chat_input("Ask a question.")

    if question:
        print("question is : ", question)
        with st.chat_message("user"):
            st.write(question)
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question,
        )

        with st.chat_message("assistant"):
            try:
                with client.beta.threads.runs.stream(
                    thread_id=thread.id,
                    assistant_id=assistant.id,
                    event_handler=EventHandler(),
                ) as stream:
                    stream.until_done()
            except Exception as e:
                st.error(f"An error occurred: {e}")
                print(e)
'''

st.code(body, language="python", line_numbers=True)