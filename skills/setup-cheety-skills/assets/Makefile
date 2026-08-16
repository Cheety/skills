# Stack-neutral entry point. Set PROFILE per repository.
PROFILE ?= laravel

.PHONY: pruefe arch arch-eval alle-profile zyklus-pruefung forge skill-eval

pruefe: arch arch-eval skill-eval forge     ## Full harness check

arch:                                       ## Principle rules against the application code
	python3 tools/arch-check/arch_check.py . --profile $(PROFILE)

arch-eval:                                  ## Self-test the rules of the active profile
	python3 tools/arch-check/eval.py --profile $(PROFILE)

alle-profile:                               ## Self-test every installed profile
	@for f in tools/arch-check/profiles/*.json; do \
		p=$$(basename "$$f" .json); \
		python3 tools/arch-check/eval.py --profile "$$p" || exit 1; \
	done

zyklus-pruefung:                            ## Check git history against test-first (set FIRST/THEN)
	python3 tools/skill-eval/cycle_check.py $(REPO) --test-command "$(TESTS)" \
		--first "$(or $(FIRST),Test:)" --then "$(or $(THEN),Impl:)"

forge:                                      ## forge configuration against its own syntax
	python3 tools/forge_check.py .

skill-eval:                                 ## Issue rubric
	python3 tools/skill-eval/rubric.py tools/skill-eval/results/issues
