.PHONY: clean check

check:
	codecheck *.py
	pylint *.py
clean:
	find . "(" -name "*~" -or  -name ".#*" -or -name "*.pyc" ")" -print0 | xargs -0 rm -f
