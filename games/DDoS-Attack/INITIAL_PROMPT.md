Let's build an LLM-based text adventure game for a scenario where a network is experiencing a DDoS attack.

Instead of hardcoded command trees, use a system-prompted LLM (running in Docker) to drive the interactive course using natural language. The model should evaluate user actions and decide whether the mitigation path is correct, or whether an attack succeeds.

Platform requirements:
- Include a `docker-compose.yml` that runs support services and an OSS LLM.
- The LLM should be given course story, canonical success path, and strict judging criteria.
- The LLM must handle hint/help requests without giving away full solutions.

Story:
Invent a story wher the user, the on-call network admin, is responsible for mitigating a DDoS attack. Be creative, use the web to find real world stories if that helps. Success is if the user recovers the network and mitagates the attack. It should have a max turn limit, if the max turns are reached, then the network is taken down and the attackers win and the user loses. hint/help requests count as a turn.

Terminal graphics:
Animated terminal ASCII graphics and art would really make this game interesting. Network maps, monitors, etc.. Be as creative as you can and have fun.