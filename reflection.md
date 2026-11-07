## 1. How did you break down the problem before prompting?

- I turned “build a to-do app” into specific behaviors: add, edit, delete, complete, and filter tasks, with data saved across restarts. 
- I also specified the technologies (Python, SQLite, HTML/CSS/JavaScript), asked for the codebase structure before coding, and requested setup instructions. 
- I told the AI not to run the app, so I knew I would need to check it locally afterward to control the output. 
- The resulting design separated the Flask routes, SQLite operations, and browser interface, which made it easier to locate a failure.

## 2. What did the AI get wrong, and how did you fix it?

The first version failed when I opened `/`: Flask returned a 500 error with `jinja2.exceptions.TemplateNotFound: index.html`. The AI had created `templates/index.html` at the project root but initialized Flask from the `todo` package. Flask therefore looked for the template under `todo/templates/`. 
I supplied the full traceback and asked the AI to explain the cause. The fix in `todo/__init__.py` sets Flask's root path to the project folder and its instance path to the project's `instance` folder, so the template, static assets, and database paths match the actual structure. The development-server warning in the log was informational; the missing template caused the 500.

## 3. What did you deliberately not delegate to AI, and why?

- I decided the minimum features and technology constraints myself. 
- I also kept the first local run and error report in my hands: I asked the AI to write code without running it, then used the real server output to challenge its assumption that the app was ready. 

This matters because generated code can look complete while a path or configuration mistake prevents it from starting. I have not yet claimed that every task flow works in the browser; the traceback and path fix only address the page-loading error.

## 4. What would you do differently with more time?
- I think I need to be more specific with my prompts regarding UI/UX—tailoring the interface design to suit different types of users.
- I will integrate a chatbot to help handle tasks directly within the app.
- Maybe I will deploy it with vercal app.
