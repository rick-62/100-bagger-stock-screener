
local:
	samlocal validate --template 100-bagger-stock-screener/template.yaml
	samlocal build --template 100-bagger-stock-screener/template.yaml
	samlocal deploy --guided

deploy:
	sam validate --template 100-bagger-stock-screener/template.yaml
	sam build --template 100-bagger-stock-screener/template.yaml
	sam deploy --guided

loop:
	pytest --looponfail