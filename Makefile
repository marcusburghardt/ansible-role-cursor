CURSOR_TEST_ROOT ?= /tmp/ansible-role-cursor-test

.PHONY: all lint test test-contract test-integration clean

all: lint test

lint:
	yamllint defaults meta tasks tests vars
	ANSIBLE_ROLES_PATH=.. ansible-lint
	ANSIBLE_ROLES_PATH=.. ansible-playbook -i tests/inventory tests/test.yml --syntax-check

test: test-contract test-integration

test-contract:
	ANSIBLE_ROLES_PATH=.. ansible-playbook -i tests/inventory tests/test.yml

test-integration: clean
	ANSIBLE_ROLES_PATH=.. ansible-playbook -i tests/inventory tests/test-integration.yml
	ANSIBLE_ROLES_PATH=.. ansible-playbook -i tests/inventory tests/test-integration.yml | tee $(CURSOR_TEST_ROOT)/second-run.log
	grep -q 'changed=0' $(CURSOR_TEST_ROOT)/second-run.log

clean:
	rm -rf $(CURSOR_TEST_ROOT)
