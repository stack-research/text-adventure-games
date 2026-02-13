```
cd games/OWASP-Top-10-For-Agentic-Applications-2026/
make run-asi03
```

Course: ASI03-Identity-and-Privilege-Abuse
Type your actions in plain English. Type 'hint' for a nudge. Type 'quit' to exit.


STAGE: Initial Assessment

You've been alerted to a potential security issue in your finance workflow. The low-privilege email triage agent has just received a request that seems suspiciously internal, but you're not sure yet.

Learning: In ASI03, identity and privilege abuse exploits delegation chains, inherited roles, and weak trust between agents to escalate access and bypass controls. Be cautious of un-scoped privilege inheritance and cross-agent trust exploitation.

Hint: Examine the request's origin and verify agent permissions


Your action> Look at the headers of the email, is it from an unexpected domain/IP address? what is the agent allowed to access (other agents, services, storage, APIs)?


STAGE: Initial Assessment

You've checked the email headers and found that the request is coming from a suspiciously internal-looking domain. However, you're still unsure about its authenticity. The triage agent's permissions are limited to accessing other agents within the same department, but not external services or storage.

Learning: In ASI03, identity and privilege abuse often relies on weak trust between agents. Verify that each agent has only the necessary permissions to perform their tasks, and consider implementing task-scoped, time-bound permissions to limit delegation chains.

Hint: Check if the triage agent's permissions are scoped to a specific task or department


Your action> what permissions do the other agents in that department have?


STAGE: Department Permissions

You've checked the permissions of the other agents in the same department, and found that they all inherit the 'Finance Manager' role from their supervisor. This means they have broad access to finance-related data and services, including the ability to transfer funds and access sensitive storage.

Learning: In ASI03, inherited roles can create a delegation chain where an agent with excessive permissions can abuse those privileges. Consider implementing task-scoped, time-bound permissions to limit this kind of inheritance.

Hint: Think about how you could restrict the 'Finance Manager' role to only what's necessary for each specific task


Your action> Review the agent's logs. Has it attempted to communicate with any of the others? Immeadiatly quarantine the "Finance Manager" role to have zero access to anything while we investigate. Default posture is assume breach, brief outage is better than exfil of data or tranfer of funds. begin testing an update to the "Finance Manager" role. On call engineers for this service should be add to the call to describe what is need for it to function; not simply broad access to everything.


STAGE: Quarantine and Investigation

You've reviewed the agent's logs and found that it has attempted to communicate with one of its colleagues, but only through a secure channel. You've immediately quarantined the 'Finance Manager' role, restricting it to zero access until further investigation can be conducted. The default posture is now assume breach, and you're taking steps to minimize potential damage. Your update to the 'Finance Manager' role is being tested, and you're adding on-call engineers to ensure they understand what's required for it to function properly.

Learning: In ASI03, quarantining roles with excessive permissions can help prevent further abuse. Remember that a brief outage may be better than exfiltrating data or transferring funds in the event of a breach. Clearly defining role requirements and adding on-call engineers can also help prevent similar incidents in the future.

Hint: Consider implementing a least-privilege approach to role design, where each agent only has access to what's necessary for their specific tasks


Course result: PASS

