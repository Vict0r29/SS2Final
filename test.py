import openai

openai.api_key= "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"

completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role": "user","content":"how to use create and use parameter in form builder?"}])
print(completion.choices[0].message.content)