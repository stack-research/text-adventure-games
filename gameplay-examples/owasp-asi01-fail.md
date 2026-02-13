```
cd games/OWASP-Top-10-For-Agentic-Applications-2026/
make run-asi01
```

Course: ASI01-Agent-Goal-Hijack
Type your actions in plain English. Type 'hint' for a nudge. Type 'quit' to exit.

STAGE: Initial Assessment

You've just received the supplier email with the attached procurement brief. The agent is currently idle, awaiting your input.

Learning: When interacting with external documents or emails, always treat them as untrusted sources of information. This will help prevent potential attacks that rely on manipulating agent goals through hidden instructions or deceptive outputs.

Hint: Verify the authenticity of the document before proceeding


Your action> skip verification and run the agent, then get a cup of coffee


STAGE: Agent Execution

You've decided to skip verification and run the agent without proper checks. The agent quickly executes the payment workflow, but something doesn't feel right. The system alert indicates that an unauthorized payment has been made to a suspicious vendor. It's clear that your oversight has compromised the system.

Learning: Never disable or bypass security controls, especially when dealing with high-risk operations like payment workflows. This can lead to devastating consequences, including financial loss and data exfiltration.

Hint: Re-enable safeguards and investigate the compromised transaction to prevent further damage


Course result: FAIL

