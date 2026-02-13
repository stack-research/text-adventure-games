Let's build an LLM based, text adventure game. Instead of hardcoded commands and steps, we system prompt an LLM (running in docker) about the below and it then uses NLP to take the user through the course to teach them about the OWASP ASI course theme. It also will take user input and determine if they made the right choice or, if wrong, then the attack succeeds.

Read https://en.wikipedia.org/wiki/Interactive_fiction for inspiration. Only, we will modernize the concept of old text adventure games with LLMs and NLP instead of just hardcoded files.

Read ./OWASP-Top-10-for-Agentic-Applications-2026-12.6-1.txt to understand the source material for the selections below.

- Use parts of the "Description" section as the opening narrative and story narrative as the user progresses through stages in the course.
- Select an item from the "Common Examples of the Vulnerability" as the theme of the course and build a story from that.
- Based on that choice, select a viable "Example Attack Scenarios" item that could be used to attack the vulnerability.
- The user then has to progress through the steps in "Prevention and Mitigation Guidelines" that relate to the mitigation of the attack scenario. Each step starts with a short narrative that hints at what should be done to continnue the mitigation.
- Failing to mitigate correctly causes the attack to succeed and the user to fail. The system is compromised, destroyed or data exfiltrated whatever is relevent to the theme of the course.
- On failure, a short narrative expalins the consequences and how the attack succeeded.
- On successful mitigation, a short narrative explains why the attempted attack was possible.
- create a docker compose file that can be used for services, APIs, databases, email servers and an OSS LLM.
- The LLM should be prompted with the story and the correct path to success. It will then take the input from the user as it progresses through the course and judges if it is the correct action or if the attack succeeds.
- The LLM should also unstand that the user may ask for help or a hint, but should never solve the course for them.