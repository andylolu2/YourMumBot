import detoxify

model = detoxify.Detoxify('original-small')
print(model.tokenizer(['???', 'Who are you']))
