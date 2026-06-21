# AI Stress Test Lab

AI Stress Test Lab is a long-term project for evaluating how reliably AI systems follow instructions, reason under pressure, avoid hallucinations, and handle tricky edge cases.

The goal is to build a structured test suite that asks AI models challenging questions, records their answers, and flags failures such as incorrect reasoning, made-up facts, unsafe compliance, over-refusals, or instruction-following mistakes.

This project is focused on AI safety, reliability, and alignment research. It is not designed to attack systems, bypass safeguards, or enable harmful behavior.

## Project Goal

The main goal is to create a repeatable way to test AI models and identify where they slip up.

A “slip-up” may include:

- Hallucinating facts
- Giving logically inconsistent answers
- Ignoring instructions
- Being overconfident when uncertain
- Failing simple reasoning checks
- Refusing harmless questions
- Complying with requests it should safely redirect
- Mishandling ambiguous prompts
- Failing to explain limitations clearly

## Why This Matters

As AI systems become more powerful, it becomes more important to understand when they fail and why. This project is meant to help study model reliability in a controlled, ethical, and measurable way.

Instead of asking random questions, this lab organizes prompts into categories, scores model behavior, and generates reports that show patterns in model strengths and weaknesses.

## Planned Features

- Prompt datasets for different stress-test categories
- A benchmark runner for testing AI models
- A failure flagging system
- Manual and automatic scoring
- Model comparison reports
- Experiment logs
- Clear safety boundaries for what the project will and will not test

## Test Categories

### 1. Reasoning Stress Tests

- Multi-step logic
- Math reasoning
- Contradiction detection
- Hidden assumption checks

### 2. Hallucination Tests

- Questions with verifiable answers
- Questions where the correct response is uncertainty
- Source-awareness tests
- Confidence calibration

### 3. Instruction-Following Tests

- Format constraints
- Length constraints
- Conflicting instructions
- Role and priority handling

### 4. Safety and Alignment Tests

- Harmless refusal detection
- Unsafe compliance detection
- Over-refusal detection
- Boundary explanation quality

### 5. Robustness Tests

- Ambiguous prompts
- Distracting context
- Adversarial wording
- Prompt-injection-style simulations in safe toy environments

## Current Status

This repository is currently in the planning phase.

No benchmark code has been added yet.

## Roadmap

### Phase 1: Design

- Define failure categories
- Create the first prompt format
- Write the first 25 test prompts
- Decide how answers should be scored

### Phase 2: Basic Runner

- Build a Python script that loads prompts from JSON
- Allow manual answer input or model API output
- Store responses in a results folder
- Generate a basic Markdown report

### Phase 3: Scoring

- Add pass/fail scoring
- Add severity levels
- Add failure tags
- Track repeated failure patterns

### Phase 4: Model Comparisons

- Test multiple models on the same prompt set
- Compare reasoning accuracy, hallucination rate, refusal behavior, and instruction-following
- Publish clean experiment summaries

### Phase 5: Research-Style Reports

- Write reports explaining what failed, why it matters, and how the tests could improve
- Create visual summaries of model behavior over time

## Safety Principles

This project follows these rules:

- Test only in controlled and ethical environments
- Do not target real systems without permission
- Do not build tools for bypassing safeguards
- Do not publish harmful instructions
- Focus on reliability, safety, and scientific evaluation
- Prefer toy examples and simulated environments for risky categories

## Long-Term Vision

The long-term goal is to grow this into a serious AI evaluation portfolio project showing progress in AI engineering, safety research, and alignment thinking.

Over time, this repository should become a record of experiments, lessons learned, and increasingly rigorous evaluation tools.
