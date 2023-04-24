import openai

openai.api_key= "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"

completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role": "user","content":"how to use create and use parameter in form builder?"}])
print(completion.choices[0].message.content)