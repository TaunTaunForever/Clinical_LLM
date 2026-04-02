# Deployment Plan

## Demo architecture

The Phase 1 target is a hybrid local-plus-remote demo:

- remote LLM planner
- local dataset
- local deterministic analytics engine
- local CLI or lightweight app wrapper

## Data handling rules

- do not send raw patient rows to the remote planner
- send only schema metadata, allowed operations, question text, and output contract
- keep all numeric computation local

## Candidate runtime layout

1. Local application receives question
2. Prompt builder formats planner request
3. Remote planner returns JSON plan
4. Local validator checks plan
5. Local execution engine runs plan
6. Optional summarizer explains computed outputs

## Phase 1 deployment scope

Phase 1 does not include containerization, cloud deployment, authentication, or a production UI. The focus is a clear local demo workflow.

## TODO

- define environment-variable-based planner credentials
- package a simple local web or CLI demo
- add reproducible local run instructions once a dataset is wired in
