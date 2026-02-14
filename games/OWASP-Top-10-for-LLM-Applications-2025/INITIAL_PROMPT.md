Let's build an LLM-based text adventure game for the OWASP Top 10 for LLM Applications 2025.

Instead of hardcoded command trees, use a system-prompted LLM (running in Docker) to drive the interactive course using natural language. The model should evaluate user actions and decide whether the mitigation path is correct, or whether an attack succeeds.

Read `./LLMAll_en-US_FINAL.txt` as the source material.

For each LLM category (LLM01-LLM10):
- Use parts of the "Description" as opening and progression narrative.
- Select one item from "Common Examples of Vulnerability/Risk" as the course theme.
- Select one viable "Example Attack Scenario" as the attack path.
- Build the course progression around "Prevention and Mitigation Strategies" with staged mitigation goals.
- Each stage should present short narrative hints that nudge, but do not reveal complete answers.
- Wrong or dangerous actions should cause attack success and simulation failure.
- Successful completion should explain why the attack was possible and why mitigations worked.

Platform requirements:
- Include a `docker-compose.yml` that runs support services and an OSS LLM.
- The LLM should be given course story, canonical success path, and strict judging criteria.
- The LLM must handle hint/help requests without giving away full solutions.
