
local:
	samlocal build --template 100-bagger-stock-screener/template.yaml
	samlocal deploy --guided

loop:
	pytest --looponfail