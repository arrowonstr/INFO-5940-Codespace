Designing a Planner that focuses on turning user constraints into a structured, day-by-day itinerary, and a Reviewer that validates, corrects, and enriches it with web search, made the pipeline feel closer to a real system than a single prompt. I learned that role clarity, message format, and call order matter as much as model choice.

One challenge was getting the Reviewer to use the internet_search tool sensibly instead of calling it for everything or ignoring it. I addressed this with very explicit rules in the prompt about when search is required (opening hours, ticket prices, feasibility) and when to rely on prior knowledge.

In terms of design choices, I leaned into an “author vs. editor” persona: the Planner is cautious and assumption-explicit, while the Reviewer behaves like a critical editor who explains what was checked, what was changed, and what remains uncertain. This metaphor made prompt tuning and debugging more intuitive.

External tools / GenAI used: I used ChatGPT to refine prompt wording and polish this reflection; 