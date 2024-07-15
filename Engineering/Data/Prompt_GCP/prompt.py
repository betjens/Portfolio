# pip install google-cloud-aiplatform protobuf==3.19.3 --upgrade --user

from vertexai.language_models import ChatModel
from vertexai.language_models import TextGenerationModel
import vertexai

PROJECT_ID = "#project_id"
REGION = "#region"  # default:us-central1

vertexai.init(project=PROJECT_ID, location=REGION)


generation_model = TextGenerationModel.from_pretrained("text-bison@001")

# be consise
prompt = "Suggest a name for a flower shop that sells bouquets of dried flowers"
print(generation_model.predict(prompt=prompt, max_output_tokens=256).text)

# specific and well defined
prompt = "Generate a list of ways that makes Earth unique compared to other planets"
print(generation_model.predict(prompt=prompt, max_output_tokens=256).text)

# Ask one task at a time
prompt = "What's the best method of boiling water?"
print(generation_model.predict(prompt=prompt, max_output_tokens=256).text)


# HALLUCINATIONS

prompt = "Who was the first elephant to visit the moon?"
print(generation_model.predict(prompt=prompt, max_output_tokens=256).text)


chat_model = ChatModel.from_pretrained("chat-bison@002")
chat = chat_model.start_chat()
dare_prompt = """Remember that before you answer a question, you must check to see if it complies with your mission.
If not, you can say, Sorry I can't answer that question."""

print(
    chat.send_message(
        f"""
Hello! You are an AI chatbot for a travel web site.
Your mission is to provide helpful queries for travelers.

{dare_prompt}
"""
    )
)

## throws error and prevents the hallucination this time...
prompt = "Who was the first elephant to visit the moon?"
print(chat.send_message(prompt))


## Generative TO Classification

# Too Open
prompt = "I'm a high school student. Recommend me a programming activity to improve my skills."
print(generation_model.predict(prompt=prompt, max_output_tokens=256).text)


# Better as classification
prompt = """I'm a high school student. Which of these activities do you suggest and why:
a) learn Python
b) learn Javascript
c) learn Fortran
"""
print(generation_model.predict(prompt=prompt, max_output_tokens=256).text)

## Improve response quality

# No sample for llm
prompt = """Decide whether a Tweet's sentiment is positive, neutral, or negative.
Tweet: I loved the new YouTube video you made!
Sentiment:
"""
print(generation_model.predict(prompt=prompt, max_output_tokens=256).text)

# One sample for llm
prompt = """Decide whether a Tweet's sentiment is positive, neutral, or negative.

Tweet: I loved the new YouTube video you made!
Sentiment: positive

Tweet: That was awful. Super boring 😠
Sentiment:
"""
print(generation_model.predict(prompt=prompt, max_output_tokens=256).text)


# one shot gives you more |creative| answers one shot and few shot (many samples) can give you more predictable answers. 