ANTLR4=antlr4
ANTLR4_PARSE=antlr4-parse

GRAMMAR=Rusty.g4
LIBS=libs


all: help


help:
	@echo 'Targets:'
	@echo "- parser - generates parser with ANTLR from grammar $(GRAMMAR)"
	@echo "- clean  - removes all generated ANTLR files from $(LIBS)"


parser: $(GRAMMAR)
	$(ANTLR4) -Dlanguage=Python3 -o $(LIBS) $<


clean:
	rm -f libs/*.interp libs/*.tokens libs/*.py
	rm -rf libs/__pycache__


.PHONY: clean
