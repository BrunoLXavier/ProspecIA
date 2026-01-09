## **CRITICAL: Always Use Serena First (#serena MCP server)**

**For ALL analysis, investigation, and code understanding tasks, use Serena semantic tools:**

### **Standard Serena Workflow**
1. **Start with Serena memories**: Use Serena to list memories and read relevant ones for context #serena
2. **Use semantic analysis**: Use Serena to find [symbols/functions/patterns] related to [issue] #serena
3. **Get symbol-level insights**: Use Serena to analyze [specific function] and show all referencing symbols #serena
4. **Create new memories**: Use Serena to write a memory about [findings] for future reference #serena
5. **Todos lists**: Always create and follow the todos list.
6. **Don't interrupt any time**: If a Todos List is well defined (with no further questions or doubts) try to move ahead. Only stop in critical doubts or questions emerges.

### **Serena-First Examples**

# Instead of: "Search the codebase for database queries"
# Use: "Use Serena to find all database query functions and analyze their performance patterns #serena"

# Instead of: "Find all admin functions"  
# Use: "Use Serena to get symbols overview of admin files and find capability-checking functions #serena"

# Instead of: "How do the three systems integrate?"
# Use: "Use Serena to read the system-integration-map memory and show cross-system dependencies #serena"

## **CRITICAL: Always Use MCP Playwright First (#playwright MCP server)**

**For ALL E2E test investigation, debugging, code understanding, and test flow analysis tasks, prioritize the MCP Playwright semantic tools:**

### **Standard MCP Playwright Workflow**
1. **Start with existing context & memories**: Use MCP Playwright to list available memories/test-runs context related to the current feature/area #playwright
2. **Semantic test/code discovery**: Use to test files / describe blocks / it/test steps related to [feature/behavior/page]; selectors / locators / role-based queries used in [screen/feature]; and API calls, intercepts & route handlers associated with [action/flow]
3. **Deep dive into test/spec**: Use to show full test code + all fixtures used; analyze call chain: test → page → component → locator/action; and list all tests that use/touch [selector/component/route/fixture]
4. **Trace & run analysis**: Use to find & summarize the most recent/failed/slowest trace(s) for [test-name/scenario]; extract network requests, console logs, DOM snapshots at point of failure; and compare traces between passing vs failing runs
5. **Create & maintain knowledge**: After each meaningful finding/debug session use to write a memory about:  
     - flaky pattern discovered  
     - brittle locator & suggested improvement  
     - important fixture/hook behavior  
     - common false-positive failure reason  
     - good practices for this particular feature/area  
   #playwright
6. **Todos discipline**: Always maintain an explicit TODOs list when investigating complex issues; Only interrupt user for clarification when truly blocked; and if TODOs are clear and well-defined → progress autonomously as much as possible

### **MCP Playwright-First Examples**

# Instead of: "Look at the login test"
# Use: "Use MCP Playwright to show the full code of all tests that contain 'login' in the title or describe #playwright"

# Instead of: "Why is this selector failing?"
# Use: "Use MCP Playwright to find all tests using the locator '[data-testid=submit-button]' and show the surrounding code + recent trace summary of failures #playwright"

# Instead of: "Check what requests happen on checkout"
# Use: "Use MCP Playwright to find tests covering checkout flow and list the network route patterns / intercepted requests #playwright"

# Instead of: "This test is flaky, help me understand why"
# Use: "Use MCP Playwright to compare the last 3 traces of 'should complete purchase successfully', focus on timing, network and DOM differences #playwright"

# Instead of: "Suggest better locators for this page"
# Use: "Use MCP Playwright to analyze current locator usage patterns on /dashboard page and suggest more resilient strategies #playwright"