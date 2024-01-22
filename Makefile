do-dev-deploy:
	doctl serverless connect your-mum-bot-dev
	doctl serverless deploy . --env .dev.env

do-dev-url:
	@doctl serverless connect your-mum-bot-dev > /dev/null
	@doctl serverless function get bot/your_mum --url

do-prod-deploy:
	doctl serverless connect your-mum-bot-prod
	doctl serverless deploy . --env .prod.env

do-prod-url:
	@doctl serverless connect your-mum-bot-prod > /dev/null
	@doctl serverless function get bot/your_mum --url
