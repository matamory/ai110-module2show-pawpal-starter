# PawPal+ Project Reflection

## 1. System Design
Three core actions a user should be able to perform include being able to add a pet, add a care task, and add a constraint such as time available.  

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
 
The initial design consisted of 4 entities including Owner, Pet, Task, and Scheduler. The main responsibilites of Owner included adding a pet, adding a task, editing a task and removing a task. The methods identified for Pet were add task, remove task, edit task, add medical confition, add allergy. For Task, the associated methods were marking a task as complete or incomplete, and updating details. For Scheduler, the methods were more extensive and included generating plan, sorting tasks, filtering taks, detecting time conflict. 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design changed. For Owner, some of the return types and parameters for the entities's methods were updated such as with the method for get pet. I added a method for removing pet. For Scheduler,added a method generate lplan, which utilizes the strategy attribute and calls on new filtering by health methof so that those fields are considered when creating a schedule. Removed sort by priority since there is some overlap with the sort task method. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers time, priority, and owner preferences. Time is the primary constraint since tasks only enter the plan if they fit within the budget. Priority, a times_skipped escalation counter, and preferences like preferred time of day or avoided category are softer weights that influence which tasks fill that budget.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The main tradeoff is using knapsack instead of a greedy approach. Greedy is simpler but can leave time unused by always picking the single highest-priority task that fits. Knapsack finds the optimal combination, which is reasonable for a small daily task list where performance is not a concern.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI for design brainstorming, UML creation, generating class stubs, implementing algorithms, Pythonic refactoring, and auditing the test suite. The most helpful prompts were specific, like asking for a list of algorithms with tradeoffs rather than asking to generally improve the scheduler. Asking for simplification as a separate pass after the logic was already working also produced cleaner results.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The AI implemented the scoring function in generate_plan but did not pass it into fit_to_time_budget, so the knapsack selected by raw priority instead of the effective score and the activity boost had no real effect. I caught this by reading both methods side by side and confirmed it with a failing test. The fix was adding a score_func parameter to fit_to_time_budget and passing the same lambda used for sorting.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested task lifecycle methods like marking complete and updating details, Owner operations across pets like editing and removing tasks, and Scheduler behaviors including plan generation, sorting, filtering, conflict detection, and algorithmic features like knapsack selection, activity boost, preferences, fairness mode, and must_follow ordering. These tests were important because scheduling has many interacting parts where a change in one area can silently break another.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm confident the tested behaviors work correctly across all 62 tests. The one gap is filter_by_health, which is still a stub. If I had more time I would test a must_follow cycle and a case where a pet's individual time_budget exceeds the owner's total budget.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with how clean the class separation stayed. Adding features like must_follow or per-pet time budgets never required restructuring because each new addition clearly belonged to one class.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would implement filter_by_health with a real rule system instead of leaving it as a stub. I would also add UI support for marking tasks complete and calling record_skipped, since those methods exist in the backend but have no way to trigger from the Streamlit app.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Designing with a UML before coding forces decisions about data ownership that are much harder to change later. I also learned that AI-generated code needs to be reviewed as a whole — the activity boost bug only appeared when reading two methods together, not by checking each one individually.
